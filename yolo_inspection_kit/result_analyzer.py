"""
检测结果分析器 - 对YOLO检测结果进行统计分析
"""

from collections import Counter
from typing import Dict, List, Any, Optional


class DetectionResult:
    """单张图片的检测结果"""
    
    def __init__(self, filename: str, detections: List[Dict[str, Any]]):
        """
        初始化检测结果
        
        Args:
            filename: 图片文件名
            detections: 检测结果列表，每项为 
                {'class_name': str, 'confidence': float, ...}
        """
        self.filename = filename
        self.detections = detections
        self.class_counts = Counter([d['class_name'] for d in detections])
    
    def get_count(self, class_name: str) -> int:
        """获取指定类别的检测个数"""
        return self.class_counts.get(class_name, 0)
    
    def get_all_counts(self) -> Dict[str, int]:
        """获取所有类别的计数"""
        return dict(self.class_counts)


class InspectionAnalyzer:
    """质检分析器"""
    
    def __init__(self, expected_counts: Dict[str, int], 
                 confidence_threshold: float = 0.6):
        """
        初始化分析器
        
        Args:
            expected_counts: 各类目的预期个数，格式 {'class_name': count}
            confidence_threshold: 置信度阈值，低于此值的检测会被过滤
        """
        self.expected_counts = expected_counts
        self.confidence_threshold = confidence_threshold
    
    def analyze(self, result: DetectionResult) -> Dict[str, Any]:
        """
        分析单张图片的检测结果
        
        Args:
            result: 检测结果
            
        Returns:
            分析结果字典，包含：
            {
                'filename': str,
                'total_detections': int,
                'status': 'PASS' | 'FAIL',
                'details': [
                    {
                        'class_name': str,
                        'expected': int,
                        'actual': int,
                        'status': 'OK' | 'LACK' | 'EXCESS',
                        'message': str
                    },
                    ...
                ],
                'summary': str
            }
        """
        counts = result.get_all_counts()
        details = []
        all_pass = True
        
        # 检查每个预期的类别
        for class_name, expected_count in self.expected_counts.items():
            actual_count = counts.get(class_name, 0)
            
            if actual_count < expected_count:
                # 漏放
                missing = expected_count - actual_count
                status = 'LACK'
                message = f"❌ {class_name}：漏放 {missing} 个（预期{expected_count}，检测{actual_count}）"
                all_pass = False
            elif actual_count > expected_count:
                # 多放
                extra = actual_count - expected_count
                status = 'EXCESS'
                message = f"⚠️  {class_name}：多放 {extra} 个（预期{expected_count}，检测{actual_count}）"
                all_pass = False
            else:
                # 正好符合
                status = 'OK'
                message = f"✅ {class_name}：检测 {actual_count} 个（符合预期）"
            
            details.append({
                'class_name': class_name,
                'expected': expected_count,
                'actual': actual_count,
                'status': status,
                'message': message
            })
        
        # 检查是否有多余的检测类别
        extra_classes = set(counts.keys()) - set(self.expected_counts.keys())
        for class_name in extra_classes:
            details.append({
                'class_name': class_name,
                'expected': 0,
                'actual': counts[class_name],
                'status': 'EXCESS',
                'message': f"⚠️  {class_name}：检测到预期外的物品 {counts[class_name]} 个"
            })
            all_pass = False
        
        # 生成摘要
        if all_pass and len(counts) > 0:
            summary = "✅ 检测通过！所有物品数量正确"
        elif len(counts) == 0:
            summary = "⚠️ 未检测到任何物体"
        else:
            lack_count = sum(1 for d in details if d['status'] == 'LACK')
            excess_count = sum(1 for d in details if d['status'] == 'EXCESS')
            summary = f"❌ 检测失败：{lack_count} 个漏放，{excess_count} 个多放"
        
        return {
            'filename': result.filename,
            'total_detections': len(result.detections),
            'status': 'PASS' if all_pass else 'FAIL',
            'details': details,
            'summary': summary
        }
    
    def analyze_batch(self, results: List[DetectionResult]) -> List[Dict[str, Any]]:
        """批量分析多张图片"""
        return [self.analyze(r) for r in results]
