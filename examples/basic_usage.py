"""
YOLO检测工具包 - 基础使用示例

所有示例均以「配置文件路径」初始化 YoloInspector。
如需通过代码参数配置，请参考 code_config_examples.py。
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path


# ============================================================================
# 依赖检查（运行任何示例前先调用）
# ============================================================================

def check_dependencies() -> bool:
    """检查必需的运行时依赖"""
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
        print("\n❌ 缺少以下依赖，请先安装：")
        for m in missing:
            print(f"   • {m}")
        return False

    print("✅ 依赖检查通过")
    return True


# ============================================================================
# 示例1：全图检测
# ============================================================================

def example_1_full_image_detection():
    """示例1：全图检测（使用配置文件）"""
    print("=" * 60)
    print("示例1：全图检测")
    print("=" * 60)

    from yolo_inspection_kit import YoloInspector

    inspector = YoloInspector('config/default_config.yaml')

    result = inspector.inspect_image(
        'test_image.jpg',
        detection_mode='full'
    )

    analysis = result['analysis']
    print(f"\n文件名：{result['filename']}")
    print(f"检测模式：{result['detection_mode']}")
    print(f"总检测数：{analysis['total_detections']}")
    print(f"检测状态：{analysis['status']}")
    print(f"摘要：{analysis['summary']}")

    print("\n详细检测结果：")
    for detail in analysis.get('details', []):
        print(f"  - {detail.get('class_name', 'Unknown')}: "
              f"期望 {detail.get('expected', '?')} 个，"
              f"实际 {detail.get('actual', '?')} 个  "
              f"[{detail.get('message', '')}]")

    if result.get('annotated_image') is not None:
        save_path = inspector.save_result_image(
            result['annotated_image'],
            result['filename']
        )
        print(f"\n💾 检测结果已保存：{save_path}")


# ============================================================================
# 示例2：多ROI区域检测
# ============================================================================

def example_2_roi_detection():
    """示例2：多ROI区域检测（使用配置文件）"""
    print("\n" + "=" * 60)
    print("示例2：多ROI区域检测")
    print("=" * 60)

    from yolo_inspection_kit import YoloInspector

    inspector = YoloInspector('config/default_config.yaml')

    result = inspector.inspect_image(
        'test_image.jpg',
        detection_mode='roi'
    )

    analysis = result['analysis']
    print(f"\n文件名：{result['filename']}")
    print(f"检测模式：{result['detection_mode']}")
    print(f"总检测数：{result.get('total_detections', 0)}")
    print(f"检测状态：{analysis['status']}")
    print(f"摘要：{analysis['summary']}")

    print("\n各类目检测详情：")
    for detail in analysis.get('details', []):
        print(f"  - {detail.get('class_name', 'Unknown')}: "
              f"期望 {detail.get('expected', '?')} 个，"
              f"实际 {detail.get('actual', '?')} 个  "
              f"[{detail.get('message', '')}]")

    print("\n各ROI区域详情：")
    for roi_info in result.get('roi_details', []):
        print(f"\n  {roi_info['name']}:")
        detections = roi_info.get('detections', [])
        if detections:
            for d in detections:
                print(f"    - {d['class_name']}: {d['confidence']:.2f}")
        else:
            print("    - 无检测结果")

    if result.get('annotated_image') is not None:
        save_path = inspector.save_result_image(
            result['annotated_image'],
            result['filename']
        )
        print(f"\n💾 检测结果已保存：{save_path}")


# ============================================================================
# 示例3：批量检测
# ============================================================================

def example_3_batch_detection():
    """示例3：批量检测多张图片"""
    print("\n" + "=" * 60)
    print("示例3：批量检测")
    print("=" * 60)

    from yolo_inspection_kit import YoloInspector

    inspector = YoloInspector('config/default_config.yaml')

    test_dir = 'test_images'
    if not os.path.exists(test_dir):
        print(f"⚠️  测试目录 {test_dir} 不存在，跳过此示例")
        return

    image_files = [
        f for f in os.listdir(test_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
    ]
    print(f"共找到 {len(image_files)} 张图片")

    results_summary = []

    for image_file in image_files:
        image_path = os.path.join(test_dir, image_file)
        try:
            result = inspector.inspect_image(image_path, detection_mode='full')
            analysis = result['analysis']
            results_summary.append({
                'filename': result['filename'],
                'status':   analysis['status'],
                'total':    analysis['total_detections'],
            })
            print(f"\n✅ {image_file}")
            print(f"   状态：{analysis['status']}")
            print(f"   摘要：{analysis['summary']}")
        except Exception as e:
            print(f"\n❌ {image_file}  错误：{e}")

    print("\n" + "=" * 60)
    print("批量检测汇总")
    print("=" * 60)
    pass_count = sum(1 for r in results_summary if r['status'] == 'PASS')
    print(f"总数：{len(results_summary)}  通过：{pass_count}  失败：{len(results_summary) - pass_count}")


# ============================================================================
# 示例4：获取模型信息
# ============================================================================

def example_4_model_info():
    """示例4：获取模型信息"""
    print("\n" + "=" * 60)
    print("示例4：获取模型信息")
    print("=" * 60)

    from yolo_inspection_kit import YoloInspector

    inspector = YoloInspector('config/default_config.yaml')
    model_info = inspector.get_model_info()

    print(f"\n模型路径：{model_info['model_path']}")
    print(f"模型名称：{model_info['model_name']}")
    print(f"类别数  ：{model_info['num_classes']}")
    print("\n支持的类别：")
    for class_id, class_name in model_info['class_names'].items():
        print(f"  {class_id}: {class_name}")


# ============================================================================
# 入口
# ============================================================================

if __name__ == '__main__':
    print("YOLO 检测工具包 - 基础使用示例\n")

    if not check_dependencies():
        sys.exit(1)

    # 取消注释以运行对应示例
    # example_1_full_image_detection()
    # example_2_roi_detection()
    # example_3_batch_detection()
    # example_4_model_info()

    print("\n💡 提示：修改图片路径后取消注释对应示例即可运行")
    print("💡 如需通过代码参数配置，请参考 code_config_examples.py")