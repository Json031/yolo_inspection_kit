"""
配置加载器 - 从YAML/JSON配置文件加载检测参数
支持代码参数覆盖配置文件中的值
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径（支持 .yaml/.yml/.json），可选
            **kwargs: 代码参数，会覆盖配置文件中的值
            
        Example:
            # 方式1: 仅使用配置文件
            config = ConfigLoader('config.yaml')
            
            # 方式2: 通过参数直接配置（无需配置文件）
            config = ConfigLoader(
                model_path='./best.pt',
                save_dir='./results',
                expected_counts={'apple': 5, 'orange': 3},
                confidence_threshold=0.6
            )
            
            # 方式3: 配置文件 + 参数覆盖
            config = ConfigLoader(
                'config.yaml',
                model_path='./custom_model.pt',  # 覆盖配置文件中的值
                confidence_threshold=0.7
            )
            
        Raises:
            FileNotFoundError: 配置文件不存在且未提供必要参数
            ValueError: 配置文件格式不支持或缺少必要参数
        """
        self.config_file = Path(config_file) if config_file else None
        self.overrides = kwargs  # 保存代码参数
        
        # 首先加载配置文件内容（如果提供）
        if self.config_file:
            if not self.config_file.exists():
                raise FileNotFoundError(f"配置文件不存在：{config_file}")
            self.config = self._load_config()
        else:
            self.config = {}
        
        # 然后应用代码参数覆盖（优先级更高）
        self.config.update(self.overrides)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        suffix = self.config_file.suffix.lower()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            if suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式：{suffix}，仅支持 .yaml / .json")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def get_model_path(self) -> str:
        """
        获取模型路径
        优先级: 代码参数 > 环境变量 > 配置文件 > 异常
        """
        # 优先级1: 环境变量
        path = os.getenv('YOLO_MODEL_PATH')
        if path:
            return str(Path(path).expanduser().resolve())
        
        # 优先级2: 配置字典
        path = self.config.get('model_path')
        if not path:
            raise ValueError("缺少 'model_path' 参数。请通过以下方式之一设置：\n"
                           "1. 代码参数：YoloInspector(..., model_path='./best.pt')\n"
                           "2. 环境变量：export YOLO_MODEL_PATH='./best.pt'\n"
                           "3. 配置文件：在 YAML 中设置 model_path")
        # 支持相对路径和 ~ 扩展
        return str(Path(path).expanduser().resolve())
    
    def get_save_dir(self) -> str:
        """
        获取保存目录
        优先级: 代码参数 > 环境变量 > 配置文件 > 默认值 ./detection_results
        """
        # 优先级1: 环境变量
        path = os.getenv('YOLO_SAVE_DIR')
        if path:
            path_obj = Path(path).expanduser().resolve()
            path_obj.mkdir(parents=True, exist_ok=True)
            return str(path_obj)
        
        # 优先级2: 配置字典（使用提供的值或默认值）
        path = self.config.get('save_dir', './detection_results')
        path_obj = Path(path).expanduser().resolve()
        path_obj.mkdir(parents=True, exist_ok=True)
        return str(path_obj)
    
    def get_roi_definitions(self) -> list:
        """获取ROI定义列表"""
        roi_list = self.get('roi_definitions', [])
        if not roi_list:
            return []
        return roi_list
    
    def get_roi_colors(self) -> list:
        """获取ROI颜色列表"""
        colors = self.get('roi_colors', [])
        if not colors:
            # 返回默认颜色
            return [
                (0, 255, 0),   (0, 0, 255),   (255, 0, 0),
                (255, 255, 0), (0, 255, 255), (255, 0, 255)
            ]
        return colors
    
    def get_expected_counts(self) -> Dict[str, int]:
        """
        获取各类目的预期个数
        优先级: 代码参数 > 配置文件 > 异常
        
        Example:
            # 方式1: 通过代码参数
            config = ConfigLoader(expected_counts={'apple': 5, 'orange': 3})
            
            # 方式2: 通过配置文件
            config = ConfigLoader('config.yaml')  # config.yaml中定义expected_counts
        """
        counts = self.config.get('expected_counts')
        if not counts:
            raise ValueError("缺少 'expected_counts' 参数。请通过以下方式之一设置：\n"
                           "1. 代码参数：YoloInspector(..., expected_counts={'apple': 5})\n"
                           "2. 配置文件：在 YAML 中设置 expected_counts")
        return counts
    
    def get_confidence_threshold(self) -> float:
        """获取置信度阈值"""
        return self.get('confidence_threshold', 0.6)
    
    def get_model_predict_conf(self) -> float:
        """获取模型预测置信度阈值"""
        return self.get('model_predict_conf', 0.8)
    
    def get_audio_alerts_enabled(self) -> bool:
        """是否启用音频提醒"""
        return self.get('audio_alerts_enabled', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转为字典"""
        return self.config.copy()
