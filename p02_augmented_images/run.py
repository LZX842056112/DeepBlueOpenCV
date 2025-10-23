#!/usr/bin/env python3
# 以上声明是 Unix/Linux/macOS 系统中的标准做法，指定要使用的解释器为 Python 3
"""
图片增强工具启动脚本
"""

import os
import sys

def check_dependencies():
    """检查依赖是否安装"""
    # 必需包列表
    required_packages = ['opencv-python', 'gradio', 'numpy', 'Pillow']
    # 缺失包列表
    missing_packages = []
    
    # 检查每个包是否能成功导入，将缺失的包记录到 missing_packages 列表中
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'gradio':
                import gradio
            elif package == 'numpy':
                import numpy
            elif package == 'Pillow':
                from PIL import Image
        except ImportError:
            missing_packages.append(package)
    
    # 返回缺失包列表
    return missing_packages

def main():
    print("=" * 50)
    print("图片增强工具 - 深度学习数据增强")
    print("=" * 50)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 检查 images 目录
    if not os.path.exists("images"):
        print("警告: images目录不存在，正在创建...")
        os.makedirs("images")
        print("请在images目录中放入需要增强的图片")
    
    print("依赖检查通过！")
    print("启动Gradio界面...")
    
    # 导入并启动主程序
    from image_augmentation import create_gradio_interface
    
    # 创建 Gradio 网页界面
    demo = create_gradio_interface()
    print("服务已启动，请在浏览器中访问显示的URL")
    print("按 Ctrl+C 停止服务")
    
    # 服务启动和异常处理
    try:
        demo.launch(share=False, server_name="0.0.0.0", show_error=True)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()
