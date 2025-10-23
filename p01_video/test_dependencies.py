try:
    import cv2
    print(f"OpenCV 安装成功 - 版本: {cv2.__version__}")
except ImportError as e:
    print(f"OpenCV 安装失败: {e}")

try:
    import gradio as gr
    print(f"Gradio 安装成功 - 版本: {gr.__version__}")
except ImportError as e:
    print(f"Gradio 安装失败: {e}")

try:
    import numpy as np
    print(f"NumPy 安装成功 - 版本: {np.__version__}")
except ImportError as e:
    print(f"NumPy 安装失败: {e}")

print("\n依赖包检查完成！")
