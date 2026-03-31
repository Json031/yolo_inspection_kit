#!/usr/bin/env python3
"""
Quick validation script for yolo_inspection_kit installation and configuration.
Checks if all dependencies are available and config files are properly formatted.
"""

import sys
import json
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements."""
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'ultralytics',
        'cv2',  # opencv-python
        'numpy',
        'PIL',  # pillow
        'yaml'  # pyyaml
    ]
    
    all_installed = True
    print("\n📦 Checking dependencies:")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - not installed")
            all_installed = False
    
    return all_installed

def check_package_import():
    """Check if yolo_inspection_kit can be imported."""
    print("\n🔍 Checking yolo_inspection_kit import:")
    try:
        from yolo_inspection_kit import YoloInspector, ConfigLoader
        print("  ✅ YoloInspector imported")
        print("  ✅ ConfigLoader imported")
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def check_config_file(config_path):
    """Check if config file exists and is properly formatted."""
    print(f"\n📄 Checking config file: {config_path}")
    
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"  ❌ Config file not found: {config_path}")
        return False
    
    print(f"  ✅ Config file exists")
    
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        required_fields = ['model_path', 'expected_counts']
        for field in required_fields:
            if field in config:
                print(f"  ✅ {field} defined")
            else:
                print(f"  ⚠️  {field} missing (optional)")
        
        return True
    except yaml.YAMLError as e:
        print(f"  ❌ YAML parsing error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading config: {e}")
        return False

def check_model_file(model_path):
    """Check if model file exists."""
    print(f"\n🤖 Checking model file: {model_path}")
    
    model_file = Path(model_path).expanduser()
    if model_file.exists():
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ Model file exists ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ❌ Model file not found: {model_file}")
        return False

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("🚀 YOLO Inspection Kit - Setup Validator")
    print("=" * 60)
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Package Import': check_package_import(),
    }
    
    # Check config file if it exists
    config_path = Path(__file__).parent.parent / 'config' / 'default_config.yaml'
    if config_path.exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        checks['Config File'] = check_config_file(str(config_path))
        
        # Check model file if path is configured
        if 'model_path' in config:
            model_path = config['model_path']
            if model_path != "./models/best.pt":  # Skip default placeholder
                checks['Model File'] = check_model_file(model_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("\n🎉 All checks passed! Ready to use yolo_inspection_kit")
    else:
        print("\n⚠️  Some checks failed. Please review above messages.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
