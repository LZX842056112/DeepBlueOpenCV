# !/usr/bin/env python3
"""
测试依赖包是否安装成功
"""


def test_dependencies():
    packages = {
        'opencv-python': 'cv2',
        'gradio': 'gradio',
        'numpy': 'numpy',
        'Pillow': 'PIL'
    }

    print("正在测试依赖包...")
    print("=" * 40)

    all_installed = True
    for package_name, import_name in packages.items():
        try:
            if import_name == 'cv2':
                import cv2
                version = cv2.__version__
            elif import_name == 'gradio':
                import gradio
                version = gradio.__version__
            elif import_name == 'numpy':
                import numpy
                version = numpy.__version__
            elif import_name == 'PIL':
                from PIL import Image
                version = Image.__version__

            print(f"[成功] {package_name}: {version}")

        except ImportError as e:
            print(f"[失败] {package_name}: 未安装")
            all_installed = False

    print("=" * 40)
    if all_installed:
        print("所有依赖包安装成功！")
        return True
    else:
        print("缺少某些依赖包，请运行: pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    test_dependencies()