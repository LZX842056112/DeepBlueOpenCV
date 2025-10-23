# Cline编程过程

## 提示词

使用Python、OpenCV编程创建一个项目，实现从摄像机获取视频、保存摄像机的视频流、视频文件读取等功能，要求使用Gradio作为前端。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 检查依赖包

检查依赖包是否安装成功

```bash
python -c "import cv2; import gradio; import numpy; print('所有依赖包安装成功')"

python -c "import cv2; print('OpenCV版本', cv2.__version__)"
```

## 端口被占用

端口7860已经被占用了，停止之前的进程并使用不同的端口：

```bash
taskkill /f /im python.exe
```

