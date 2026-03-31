"""
YOLO检测工具包 - 用于产品包装清单检测、质量检查等应用场景

主要功能：
- 图片单次检测
- 多ROI区域独立检测
- 检测结果分析与统计
- 漏放/多放判断
- 音频播放反馈
"""

__version__ = "1.0.0"
__author__ = "MorganChen"

from .core import YoloInspector
from .config_loader import ConfigLoader

__all__ = [
    "YoloInspector",
    "ConfigLoader",
]
