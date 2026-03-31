"""
核心检测类 - 基于YOLO模型的检测逻辑
"""

import os
import cv2
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

try:
    from ultralytics import YOLO
except ImportError:
    raise ImportError("请先安装 ultralytics：pip install ultralytics")

from .config_loader import ConfigLoader
from .result_analyzer import DetectionResult, InspectionAnalyzer


class YoloInspector:
    """YOLO检测检查器"""
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        初始化检测器
        
        Args:
            config_file: 配置文件路径（.yaml 或 .json），可选
            **kwargs: 代码参数，会覆盖配置文件中的值
            
        Example 1: 仅使用配置文件
            inspector = YoloInspector('config/inspection_config.yaml')
            
        Example 2: 不用配置文件，直接通过代码参数
            inspector = YoloInspector(
                model_path='./models/best.pt',
                save_dir='./results',
                expected_counts={'apple': 5, 'orange': 3},
                confidence_threshold=0.6
            )
            
        Example 3: 配置文件 + 参数覆盖
            inspector = YoloInspector(
                'config/base_config.yaml',
                model_path='./custom_model.pt',  # 覆盖
                confidence_threshold=0.7         # 覆盖
            )
        """
        # 加载配置（支持可选的配置文件和代码参数）
        self.config = ConfigLoader(config_file, **kwargs)
        
        # 加载YOLO模型
        model_path = self.config.get_model_path()
        self.model = YOLO(model_path)
        
        # 获取配置参数
        self.save_dir = self.config.get_save_dir()
        self.roi_definitions = self.config.get_roi_definitions()
        self.roi_colors = self.config.get_roi_colors()
        self.expected_counts = self.config.get_expected_counts()
        self.confidence_threshold = self.config.get_confidence_threshold()
        self.model_predict_conf = self.config.get_model_predict_conf()
        
        # 初始化分析器
        self.analyzer = InspectionAnalyzer(
            self.expected_counts,
            self.confidence_threshold
        )
        
        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        
        # 初始化ROI相关
        self.rois = []  # 实际像素坐标
    
    def inspect_image(self, image_path: str, 
                      detection_mode: str = 'full') -> Dict[str, Any]:
        """
        检测单张图片
        
        Args:
            image_path: 图片文件路径
            detection_mode: 检测模式 'full' (全图) 或 'roi' (多ROI)
            
        Returns:
            检测结果字典
        """
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片：{image_path}")
        
        filename = os.path.basename(image_path)
        
        if detection_mode == 'roi' and self.roi_definitions:
            return self._inspect_with_roi(img, filename)
        else:
            return self._inspect_full_image(img, filename)
    
    def _inspect_full_image(self, img, filename: str) -> Dict[str, Any]:
        """全图检测"""
        # YOLO预测
        results = self.model.predict(
            source=img,
            save=False,
            conf=self.model_predict_conf,
            verbose=False
        )
        result_obj = results[0]
        
        # 解析检测结果
        detections = []
        for box in result_obj.boxes:
            cls_id = int(box.cls)
            class_name = self.model.names[cls_id]
            conf = float(box.conf)
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            
            if conf >= self.confidence_threshold:
                x1, y1, x2, y2 = [round(v, 3) for v in xyxy]
                detections.append({
                    'class_id': cls_id,
                    'class_name': class_name,
                    'confidence': round(conf, 3),
                    'bbox': [x1, y1, x2, y2],  # xyxy
                    'wh': [round(x2 - x1, 3), round(y2 - y1, 3)]
                })
        
        # 分析结果
        detection_result = DetectionResult(filename, detections)
        analysis = self.analyzer.analyze(detection_result)
        
        return {
            'filename': filename,
            'detection_mode': 'full_image',
            'detections': detections,
            'analysis': analysis,
            'annotated_image': result_obj.plot()  # 带检测框的图片
        }
    
    def _inspect_with_roi(self, img, filename: str) -> Dict[str, Any]:
        """多ROI检测"""
        h, w = img.shape[:2]
        
        # 计算ROI像素坐标
        if len(self.rois) == 0:
            self.rois = []
            for roi_def in self.roi_definitions:
                x1 = int(roi_def['x'] * w)
                y1 = int(roi_def['y'] * h)
                x2 = int((roi_def['x'] + roi_def['w']) * w)
                y2 = int((roi_def['y'] + roi_def['h']) * h)
                self.rois.append((x1, y1, x2, y2))
        
        # 用于绘制的画布
        annotated_frame = img.copy()
        
        # 所有检测结果汇总
        all_detections = []
        roi_details = []
        
        # 逐ROI独立检测
        for roi_idx, (x1, y1, x2, y2) in enumerate(self.rois):
            roi_crop = img[y1:y2, x1:x2]
            
            # 对每个ROI独立预测
            results = self.model.predict(
                source=roi_crop,
                save=False,
                conf=self.model_predict_conf,
                verbose=False
            )
            result_obj = results[0]
            
            roi_name = self.roi_definitions[roi_idx]['name']
            roi_info = {
                'name': roi_name,
                'roi_index': roi_idx,
                'detections': []
            }
            
            # 处理该ROI的检测结果
            for box in result_obj.boxes:
                cls_id = int(box.cls)
                class_name = self.model.names[cls_id]
                conf = float(box.conf)
                
                if conf >= self.confidence_threshold:
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    # 坐标映射回原图
                    x1_orig = x1 + xyxy[0]
                    y1_orig = y1 + xyxy[1]
                    x2_orig = x1 + xyxy[2]
                    y2_orig = y1 + xyxy[3]
                    
                    detection = {
                        'class_id': cls_id,
                        'class_name': class_name,
                        'confidence': round(conf, 3),
                        'bbox': [
                            round(x1_orig, 3),
                            round(y1_orig, 3),
                            round(x2_orig, 3),
                            round(y2_orig, 3)
                        ],
                        'wh': [
                            round(x2_orig - x1_orig, 3),
                            round(y2_orig - y1_orig, 3)
                        ],
                        'roi_name': roi_name
                    }
                    all_detections.append(detection)
                    roi_info['detections'].append(detection)
            
            roi_details.append(roi_info)
            
            # 在原图上绘制ROI边框
            self._draw_roi_box(annotated_frame, roi_idx, roi_name)
        
        # 分析全局结果
        detection_result = DetectionResult(
            filename,
            all_detections
        )
        analysis = self.analyzer.analyze(detection_result)
        
        return {
            'filename': filename,
            'detection_mode': 'multi_roi',
            'total_detections': len(all_detections),
            'roi_details': roi_details,
            'detections': all_detections,
            'analysis': analysis,
            'annotated_image': annotated_frame
        }
    
    def _draw_roi_box(self, image, roi_idx: int, roi_name: str):
        """在图片上绘制ROI边框"""
        if roi_idx >= len(self.rois):
            return
        
        x1, y1, x2, y2 = self.rois[roi_idx]
        color = self.roi_colors[roi_idx % len(self.roi_colors)]
        
        # 绘制边框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 4)
        
        # 绘制文字标签
        cv2.putText(
            image,
            roi_name,
            (x1 + 15, y1 + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            color,
            3
        )
    
    def save_result_image(self, annotated_image, filename: str) -> str:
        """
        保存检测结果图片
        
        Args:
            annotated_image: 带检测框的图片
            filename: 原始文件名
            
        Returns:
            保存路径
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.splitext(filename)[0]
        save_path = os.path.join(
            self.save_dir,
            f"{timestamp}_{basename}_detection.jpg"
        )
        
        cv2.imwrite(save_path, annotated_image)
        return save_path
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            'model_path': str(self.config.get_model_path()),
            'model_name': self.model.model_name,
            'num_classes': len(self.model.names),
            'class_names': dict(self.model.names)
        }
