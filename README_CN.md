[English](README.md) | 中文

# YOLO 产品检测工具包 (yolo_inspection_kit)

简单易用的 YOLOv8 检测工具包，专为产品外观检测和质量检测而优化。支持多种配置方式：代码参数、配置文件、环境变量或混合方式。

## ✨ 主要特性

- 🎯 **全图检测** - 对整张图片进行一次性YOLO检测
- 🔍 **多ROI检测** - 将图片分为多个区域，对每个区域独立检测
- 📊 **智能分析** - 自动统计检测结果，判断漏放/多放
- ⚙️ **灵活配置** - 支持代码参数、配置文件、环境变量等多种方式
- 🖼️ **可视化** - 输出带检测框的结果图片
- 🚀 **易于集成** - 简洁的API，一行代码开始检测

## 📋 目录结构

```
yolo_inspection_kit/
├── README.md                           # English documentation
├── README_CN.md                        # 中文说明（本文件）
├── LICENSE                             # MIT许可证
├── setup.py                            # 安装脚本
├── pyproject.toml                      # 项目配置
├── requirements.txt                    # 依赖清单
│
├── yolo_inspection_kit/                # 核心代码包
│   ├── __init__.py
│   ├── core.py                         # YoloInspector 类
│   ├── config_loader.py                # ConfigLoader 配置加载
│   └── result_analyzer.py              # InspectionAnalyzer 分析
│
├── config/
│   └── default_config.yaml             # 配置文件模板
│
└── examples/
    └── basic_usage.py                  # 使用示例
```

## � 安装

### 基础安装

```bash
pip install yolo_inspection_kit
```

### 完整安装（包含所有依赖）

```bash
pip install yolo_inspection_kit[all]
```

### 从源码安装

```bash
git clone https://github.com/Json031/yolo_inspection_kit.git
cd yolo_inspection_kit
pip install -e .
```

## �🚀 快速开始

### 四种配置方式

#### 方式1️⃣ : 代码参数（最推荐）✨
```python
from yolo_inspection_kit import YoloInspector

# 无需配置文件，直接通过参数配置
inspector = YoloInspector(
    model_path='./models/best.pt',
    save_dir='./detection_results',
    expected_counts={
        'huasa1': 1,
        'shuilongtou1': 1,
        'jiaofa1': 1,
    },
    confidence_threshold=0.6
)

# 检测图片
result = inspector.inspect_image('test_image.jpg')
print(f"检测状态：{result['analysis']['status']}")
```

#### 方式2️⃣ : 配置文件（向后兼容）
```bash
# 1. 复制配置文件
cp config/default_config.yaml config/my_config.yaml
```

编辑 `config/my_config.yaml` 中的参数：
```yaml
model_path: "./models/best.pt"
expected_counts:
  huasa1: 1
  shuilongtou1: 1
```

Python 代码中使用：
```python
from yolo_inspection_kit import YoloInspector

inspector = YoloInspector('config/my_config.yaml')
result = inspector.inspect_image('test_image.jpg')
```

#### 方式3️⃣ : 混合方式（配置文件 + 代码参数）
```python
# 加载配置文件，但用代码参数覆盖某些值
inspector = YoloInspector(
    'config/default_config.yaml',
    model_path='./models/custom_best.pt',  # 覆盖配置文件中的值
    confidence_threshold=0.75               # 覆盖
)
result = inspector.inspect_image('test_image.jpg')
```

#### 方式4️⃣ : 环境变量（生产部署推荐）
```bash
# 设置环境变量
export YOLO_MODEL_PATH="./models/best.pt"
export YOLO_SAVE_DIR="./detection_results"

# Python代码
inspector = YoloInspector(
    expected_counts={'huasa1': 1, 'shuilongtou1': 1}
)
```

### 配置优先级
```
代码参数 > 环境变量 > 配置文件 > 默认值
```

## 📝 配置文件详解

### 模型路径配置

```yaml
model_path: "./models/best.pt"
```

- **支持三种路径格式**：
  - 相对路径：`./models/best.pt`
  - 绝对路径：`/Users/username/models/best.pt`
  - 用户主目录：`~/yolo_models/best.pt`

- **获取最佳模型路径**：YOLO训练完成后，在 `runs/detect/trainX/weights/best.pt`

### 预期个数配置（关键！）

```yaml
expected_counts:
  huasa1: 1              # 预期1个
  jiaofa1: 1
  shuilongtou1: 2        # 预期2个
  xixuandiban1: 1
  shengliao1: 1
  shengliaodai1: 1
```

⚠️ **重要**：`expected_counts` 中的 `class_name` **必须与模型输出完全一致**

**如何查看模型的 class_name**：
```python
from ultralytics import YOLO

model = YOLO('best.pt')
print(model.names)  # 输出：{0: 'huasa1', 1: 'jiaofa1', ...}
```

将输出中的 class names 复制到配置文件中。

### ROI区域配置

可选功能，用于在指定区域内进行检测。

```yaml
roi_definitions:
  - name: "区域1_左上"
    x: 0.05      # 从左边界开始的相对位置（0-1）
    y: 0.05      # 从上边界开始的相对位置（0-1）
    w: 0.28      # 宽度（占整图宽度百分比）
    h: 0.52      # 高度（占整图高度百分比）
    
  - name: "区域2_中上"
    x: 0.36
    y: 0.05
    w: 0.28
    h: 0.52
```

**坐标系说明**：
- 使用 **0-1 相对坐标**，自动适配各种分辨率
- (0, 0) 代表图片左上角
- (1, 1) 代表图片右下角

### ROI颜色配置

```yaml
roi_colors:
  - [0, 255, 0]      # 第一个ROI的颜色 - BGR格式
  - [255, 0, 0]      # 第二个ROI的颜色
  - [0, 0, 255]      # 第三个ROI的颜色
```

**颜色格式**：BGR（注意OpenCV使用BGR而不是RGB）
- 红色：[0, 0, 255]
- 绿色：[0, 255, 0]
- 蓝色：[255, 0, 0]
- 黄色：[0, 255, 255]

### 置信度配置

```yaml
# YOLO模型预测的置信度阈值
model_predict_conf: 0.8

# 最终过滤的置信度阈值
confidence_threshold: 0.6
```

这两个值通常设置在 0.5-0.8 之间。

## 📚 使用示例

### 示例1：全图检测

```python
from yolo_inspection_kit import YoloInspector

inspector = YoloInspector('config/my_inspection.yaml')

# 全图检测
result = inspector.inspect_image('image.jpg', detection_mode='full')

analysis = result['analysis']
print(f"总检测数: {analysis['total_detections']}")
print(f"检测状态: {analysis['status']}")  # PASS 或 FAIL
print(f"摘要: {analysis['summary']}")
```

### 示例2：多ROI检测

```python
# ROI检测模式 - 每个ROI区域独立检测
result = inspector.inspect_image('image.jpg', detection_mode='roi')

# 结果中会包含每个ROI的检测情况
for detail in result['analysis']['details']:
    print(f"{detail['class_name']}: {detail['actual']} (期望 {detail['expected']})")
```

### 示例3：批量处理

```python
from pathlib import Path

# 批量处理文件夹中的图片
image_dir = Path('./test_images')
for image_path in image_dir.glob('*.jpg'):
    result = inspector.inspect_image(str(image_path))
    
    if result['analysis']['status'] == 'PASS':
        print(f"✅ {image_path.name}")
    else:
        print(f"❌ {image_path.name}: {result['analysis']['summary']}")
```

### 示例4：获取模型信息

```python
# 查看模型详情
info = inspector.get_model_info()
print(f"模型: {info['model_name']}")
print(f"模型大小: {info['model_size']}")
print(f"类别数: {info['num_classes']}")
print(f"类别名: {info['class_names']}")
```

## 🔍 检测结果解析

检测结果为字典格式，包含：

```python
{
    'filename': 'image.jpg',
    'detection_mode': 'full',
    'detections': [
        {
            'class_id': 0,
            'class_name': 'huasa1',
            'confidence': 0.95,
            'bbox': [10, 20, 100, 120],  # [x1,y1,x2,y2]
            'wh': [90, 100]               # [width, height]
        },
        ...
    ],
    'analysis': {
        'status': 'PASS',  # 或 'FAIL'
        'total_detections': 6,
        'summary': '检测完成，所有产品正常',
        'details': [
            {
                'class_name': 'huasa1',
                'expected': 1,
                'actual': 1,
                'status': 'OK',
                'message': '✅ huasa1: 期望1个，实际1个'
            },
            {
                'class_name': 'jiaofa1',
                'expected': 1,
                'actual': 0,
                'status': 'LACK',
                'message': '❌ jiaofa1: 期望1个，实际0个（漏放）'
            },
            ...
        ]
    },
    'annotated_image': <numpy array>
}
```

## ❓ 常见问题

### Q: 如何找到最佳模型文件 best.pt？

**A:** YOLO训练完成后，查看训练输出目录：
```bash
ls runs/detect/train/weights/best.pt
```

路径通常为：
- `/path/to/YOLO/runs/detect/trainX/weights/best.pt`

将完整路径复制到配置文件的 `model_path` 字段。

### Q: 如何确认 class_name 是否正确？

**A:** 使用以下代码查看模型的类别名：
```python
from ultralytics import YOLO

model = YOLO('best.pt')
print(model.names)  # 输出所有类别名

# 如果需要查看类别ID对应关系
for idx, name in model.names.items():
    print(f"{idx}: {name}")
```

确保配置文件中的 `expected_counts` 中的 key 与输出完全一致。

### Q: class_name 不匹配会发生什么？

**A:** 如果配置文件中的 class_name 与模型不匹配：
- ❌ 该类别检测结果会被忽略
- ❌ 分析结果会显示为漏放（LACK）
- ❌ 检测状态为 FAIL

**解决方法**：
1. 运行验证脚本：`python validate_setup.py`
2. 检查模型 class_name：使用上面的代码
3. 更新配置文件使其匹配

### Q: 如何调试检测精度不佳的问题？

**A:** 逐步调试：

1. **检查置信度阈值**
   ```yaml
   confidence_threshold: 0.5  # 降低到0.5试试
   ```

2. **查看检测详情**
   ```python
   result = inspector.inspect_image('image.jpg')
   for det in result['detections']:
       print(f"{det['class_name']}: {det['confidence']:.3f}")
   ```

3. **检查ROI配置** - 确保ROI坐标正确
   ```python
   config = inspector.config_loader
   print(config.get_roi_definitions())
   ```

4. **保存标注图片** - 看看检测框是否正确
   ```python
   inspector.save_result_image(result['annotated_image'], 'debug.jpg')
   ```

### Q: 如何使用自定义的配置文件？

**A:** 创建新的配置文件并在初始化时指定：
```python
inspector = YoloInspector('config/custom_config.yaml')
```

可以为不同的产品创建不同的配置文件：
- `config/product_a.yaml` - 产品A配置
- `config/product_b.yaml` - 产品B配置
- `config/product_c.yaml` - 产品C配置

### Q: 能否在Web服务中使用？

**A:** 可以！这个库与Web框架完全兼容：

```python
from flask import Flask, request, jsonify
from yolo_inspection_kit import YoloInspector

app = Flask(__name__)
inspector = YoloInspector('config/my_inspection.yaml')

@app.route('/detect', methods=['POST'])
def detect():
    image_file = request.files['image']
    image_file.save('temp.jpg')
    
    result = inspector.inspect_image('temp.jpg')
    
    return jsonify({
        'status': result['analysis']['status'],
        'summary': result['analysis']['summary'],
        'details': result['analysis']['details']
    })
```

## 📊 性能建议

| 配置 | 推荐值 | 说明 |
|------|--------|------|
| model_predict_conf | 0.8 | 模型预测置信度 |
| confidence_threshold | 0.6 | 最终过滤置信度 |
| 图片分辨率 | 640x480+ | 太小影响精度 |
| ROI大小 | 30%以上 | ROI太小影响检测 |

## 🛠️ 验证安装

运行验证脚本检查安装状态：

```bash
python validate_setup.py
```

输出示例：
```
============================================================
🚀 YOLO Inspection Kit - Setup Validator
============================================================
✅ Python 3.10.0
 
📦 Checking dependencies:
  ✅ ultralytics
  ✅ cv2
  ✅ numpy
  ✅ PIL
  ✅ yaml

🔍 Checking yolo_inspection_kit import:
  ✅ YoloInspector imported
  ✅ ConfigLoader imported

============================================================
📊 Validation Summary
============================================================
Python Version: ✅ PASS
Dependencies: ✅ PASS
Package Import: ✅ PASS

🎉 All checks passed! Ready to use yolo_inspection_kit
```

## 📦 发布到 PyPI

如要发布到PyPI（可选）：

```bash
# 构建包
python -m build

# 上传（需要PyPI账户）
twine upload dist/*
```

## 📄 许可证

MIT License - 可自由使用和修改

## 💬 支持

如有问题，请：
1. 查看FAQ和文档
2. 运行 `validate_setup.py` 检查环境
3. 检查配置文件是否正确

## 🎯 下一步

- [ ] 使用示例测试检测功能
- [ ] 针对你的数据调整配置
- [ ] 集成到生产系统
- [ ] （可选）贡献改进意见

---

**快速链接**
- [English README](README.md)
- [配置文件示例](config/default_config.yaml)
- [使用示例代码](examples/basic_usage.py)

**祝您使用愉快！** 🚀
