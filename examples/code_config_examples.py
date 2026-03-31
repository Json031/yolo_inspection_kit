"""
YOLO检测工具包 - 代码参数配置示例

YoloInspector 通过 YAML 配置文件初始化。
「代码配置」的正确方式是：

    定义 Config 类  →  to_dict()  →  写入临时 YAML  →  YoloInspector(yaml_path)

本文件演示三种场景：
  1. 使用现有配置文件（传统方式）
  2. 完全通过代码配置（无需手动维护配置文件）  ← 推荐
  3. 混合方式：配置文件 + 代码覆盖部分字段
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path


# ============================================================================
# 依赖检查
# ============================================================================

def check_dependencies() -> bool:
    missing = []
    deps = {
        'yaml':         'PyYAML',
        'cv2':          'opencv-python',
        'ultralytics':  'ultralytics',
        'torch':        'torch',
    }
    for module_name, package_name in deps.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(f"{module_name}  →  pip install {package_name}")
    if missing:
        print("\n❌ 缺少以下依赖：")
        for m in missing:
            print(f"   • {m}")
        return False
    return True


# ============================================================================
# 工具函数：将配置字典写入临时 YAML，返回文件路径
# ============================================================================

def _write_temp_yaml(config_dict: dict) -> str:
    """将配置字典写入临时 YAML 文件，返回文件路径"""
    fd, temp_path = tempfile.mkstemp(suffix=".yaml", prefix="yolo_config_")
    try:
        with os.fdopen(fd, 'w') as f:
            yaml.dump(config_dict, f, allow_unicode=True)
        return temp_path
    except Exception:
        os.close(fd)
        raise


# ============================================================================
# 方式1：使用现有配置文件（传统方式，向后兼容）
# ============================================================================

def example_1_config_file():
    """方式1：使用现有配置文件"""
    print("=" * 70)
    print("方式1：使用配置文件（传统方式）")
    print("=" * 70)

    from yolo_inspection_kit import YoloInspector

    inspector = YoloInspector('config/default_config.yaml')
    result = inspector.inspect_image('test_image.jpg', detection_mode='full')

    analysis = result['analysis']
    print(f"检测状态：{analysis['status']}")
    print(f"摘要    ：{analysis['summary']}")


# ============================================================================
# 方式2：完全通过代码配置（推荐）
# ============================================================================

class InspectionConfig:
    """
    统一管理检测配置。
    修改此类的属性即可调整所有参数，无需手动编辑 YAML 文件。
    """

    # ---------- 模型 ----------
    model_path          = Path.home() / "Desktop" / "training_results" / "best.pt"
    model_predict_conf  = 0.8   # YOLO 推理置信度阈值
    confidence_threshold = 0.6  # 最终过滤阈值

    # ---------- 输出 ----------
    save_dir             = "./build/detection_results"
    audio_alerts_enabled = False

    # ---------- 预期数量（class_name 需与模型输出一致）----------
    expected_counts = {
        "huasa1":      1,   # 花洒
        "jiaofa1":     1,   # 胶法
        "shuilongtou1":1,   # 水龙头
        "linyuguan1":  1,   # 连衣管
        "ruanguan1":   1,   # 软管
        "shengliaodai1":1,  # 塑料袋
    }

    # ---------- ROI 区域（检测模式 roi 时生效）----------
    roi_definitions = [
        {"name": "区域1_左上", "x": 0.05, "y": 0.05, "w": 0.28, "h": 0.52},
        {"name": "区域2_中上", "x": 0.36, "y": 0.05, "w": 0.28, "h": 0.52},
        {"name": "区域3_右上", "x": 0.67, "y": 0.05, "w": 0.28, "h": 0.52},
    ]
    roi_colors = [
        [0, 255, 0],   # 绿
        [255, 0, 0],   # 蓝
        [0, 0, 255],   # 红
    ]

    @classmethod
    def to_dict(cls) -> dict:
        return {
            "model_path":           str(cls.model_path),
            "model_predict_conf":   cls.model_predict_conf,
            "confidence_threshold": cls.confidence_threshold,
            "save_dir":             cls.save_dir,
            "audio_alerts_enabled": cls.audio_alerts_enabled,
            "expected_counts":      cls.expected_counts,
            "roi_definitions":      cls.roi_definitions,
            "roi_colors":           cls.roi_colors,
        }


def example_2_code_config():
    """方式2：完全通过代码配置（推荐，无需手动维护 YAML 文件）"""
    print("=" * 70)
    print("方式2：完全通过代码配置（推荐）")
    print("=" * 70)

    from yolo_inspection_kit import YoloInspector

    temp_path = None
    try:
        # 步骤1：生成临时配置文件
        temp_path = _write_temp_yaml(InspectionConfig.to_dict())
        print(f"✅ 临时配置已生成：{temp_path}")

        # 步骤2：用临时配置初始化检测器
        inspector = YoloInspector(temp_path)

        # 步骤3：执行检测
        result = inspector.inspect_image('test_image.jpg', detection_mode='full')
        analysis = result['analysis']
        print(f"检测状态：{analysis['status']}")
        print(f"摘要    ：{analysis['summary']}")

    finally:
        # 步骤4：清理临时文件
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
            print("🗑️  临时配置文件已清理")


# ============================================================================
# 方式3：混合方式（读取配置文件，再用代码覆盖部分字段）
# ============================================================================

def example_3_mixed():
    """方式3：读取配置文件，通过代码覆盖部分字段"""
    print("=" * 70)
    print("方式3：混合方式（配置文件 + 代码覆盖）")
    print("=" * 70)

    from yolo_inspection_kit import YoloInspector

    # 加载基础配置文件
    with open('config/default_config.yaml', 'r') as f:
        base_config = yaml.safe_load(f)

    # 通过代码覆盖需要修改的字段
    overrides = {
        "model_path":           str(Path.home() / "Desktop" / "training_results" / "custom_best.pt"),
        "confidence_threshold": 0.75,
        "save_dir":             "./build/custom_results",
        "expected_counts": {
            "huasa1":      1,
            "jiaofa1":     1,
            "shuilongtou1":1,
        },
    }
    merged_config = {**base_config, **overrides}

    temp_path = None
    try:
        temp_path = _write_temp_yaml(merged_config)
        print(f"✅ 合并配置已生成：{temp_path}")
        print(f"   覆盖字段：{list(overrides.keys())}")

        inspector = YoloInspector(temp_path)
        result = inspector.inspect_image('test_image.jpg', detection_mode='full')
        analysis = result['analysis']
        print(f"检测状态：{analysis['status']}")
        print(f"摘要    ：{analysis['summary']}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# ============================================================================
# 实际场景：多产线并行检测
# ============================================================================

def example_4_multi_line():
    """场景：多条产线使用不同配置并行检测"""
    print("=" * 70)
    print("场景：多产线并行检测")
    print("=" * 70)

    from yolo_inspection_kit import YoloInspector

    # 产线1 配置
    line1_config = {
        "model_path":           str(Path.home() / "Desktop" / "training_results" / "line1_best.pt"),
        "model_predict_conf":   0.8,
        "confidence_threshold": 0.65,
        "save_dir":             "./build/results/line1",
        "audio_alerts_enabled": False,
        "expected_counts":      {"huasa1": 1, "jiaofa1": 1},
        "roi_definitions":      [],
        "roi_colors":           [],
    }

    # 产线2 配置（置信度更高，产品类别不同）
    line2_config = {
        "model_path":           str(Path.home() / "Desktop" / "training_results" / "line2_best.pt"),
        "model_predict_conf":   0.85,
        "confidence_threshold": 0.75,
        "save_dir":             "./build/results/line2",
        "audio_alerts_enabled": False,
        "expected_counts":      {"shuilongtou1": 1, "linyuguan1": 1},
        "roi_definitions":      [],
        "roi_colors":           [],
    }

    temps = []
    try:
        t1 = _write_temp_yaml(line1_config)
        t2 = _write_temp_yaml(line2_config)
        temps = [t1, t2]

        inspector1 = YoloInspector(t1)
        inspector2 = YoloInspector(t2)

        result1 = inspector1.inspect_image('line1_product.jpg', detection_mode='full')
        result2 = inspector2.inspect_image('line2_product.jpg', detection_mode='full')

        print(f"产线1 检测结果：{result1['analysis']['status']}")
        print(f"产线2 检测结果：{result2['analysis']['status']}")

    finally:
        for t in temps:
            if os.path.exists(t):
                os.unlink(t)


# ============================================================================
# 配置优先级说明
# ============================================================================

def print_config_priority_guide():
    print("=" * 70)
    print("YoloInspector 配置方式总结")
    print("=" * 70)
    print("""
初始化方式（三选一）：

  方式1 - 配置文件（传统）
    inspector = YoloInspector('config/default_config.yaml')

  方式2 - 代码配置（推荐）
    config_dict = InspectionConfig.to_dict()   # 定义 Config 类
    temp_path   = _write_temp_yaml(config_dict) # 生成临时 YAML
    inspector   = YoloInspector(temp_path)      # 初始化
    os.unlink(temp_path)                        # 用完清理

  方式3 - 混合（配置文件 + 代码覆盖）
    base_config  = yaml.safe_load(open('config/default_config.yaml'))
    merged       = {**base_config, **overrides}
    temp_path    = _write_temp_yaml(merged)
    inspector    = YoloInspector(temp_path)

检测模式：
  detection_mode='full'   全图检测（默认）
  detection_mode='roi'    多ROI区域检测
    """)


# ============================================================================
# 入口
# ============================================================================

if __name__ == '__main__':
    print_config_priority_guide()

    if not check_dependencies():
        sys.exit(1)

    # 取消注释以运行对应示例
    # example_1_config_file()   # 方式1：配置文件
    # example_2_code_config()   # 方式2：代码配置（推荐）
    # example_3_mixed()         # 方式3：混合
    # example_4_multi_line()    # 场景：多产线

    print("\n💡 取消注释上方示例函数后重新运行即可")