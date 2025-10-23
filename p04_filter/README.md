# 卷积操作可视化演示项目

这是一个使用Python、OpenCV和Gradio创建的卷积操作可视化演示项目，可以实时展示不同卷积核对图像的处理效果。

## 项目功能

- 加载并显示 `images/xiaoren.png` 图像
- 应用10种不同的卷积核操作
- 可视化卷积核矩阵
- 实时对比原始图像和处理后图像
- 可调节卷积核大小（对支持大小变化的卷积核）

## 主要方法

| 方法                        | 功能                       |
| --------------------------- | -------------------------- |
| **load_image()**            | **加载并预处理图像**       |
| **apply_convolution()**     | **应用卷积操作的核心方法** |
| get_identity_kernel()       | 单位卷积核（不改变图像）   |
| get_blur_kernel()           | 均值模糊                   |
| get_gaussian_blur_kernel()  | 高斯模糊                   |
| get_sharpen_kernel()        | 锐化                       |
| get_edge_detection_kernel() | 边缘检测                   |
| get_sobel_x_kernel()        | Sobel边缘检测（水平）      |
| get_sobel_y_kernel()        | Sobel边缘检测（垂直）      |
| get_laplacian_kernel()      | 拉普拉斯边缘检测           |
| get_emboss_kernel()         | 浮雕效果                   |
| **visualize_kernel()**      | **可视化卷积核矩阵**       |



| 函数                 | 功能               |
| -------------------- | ------------------ |
| create_interface()   | 创建 Gradio 界面   |
| process_image()      | 处理图像并返回结果 |
| update_description() | 动态更新描述       |



## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行项目

```bash
python convolution_demo.py
```

程序将在本地启动一个Gradio Web界面，默认地址为：http://localhost:7860

## 使用说明

1. 在左侧选择要应用的卷积核类型
2. 调整卷积核大小（只对支持大小变化的卷积核有效）
3. 点击"应用卷积"按钮查看效果
4. 观察右侧的卷积核矩阵可视化
5. 对比下方的原始图像和处理后图像

## 卷积核说明

- **单位卷积核**: 保持图像不变，用于基准比较
- **均值模糊**: 使用平均值平滑图像
- **高斯模糊**: 使用高斯分布进行更自然的平滑
- **锐化**: 增强图像边缘和细节
- **边缘检测**: 突出显示图像中的边缘
- **Sobel算子**: 分别检测水平和垂直方向的边缘
- **拉普拉斯**: 使用二阶导数检测边缘
- **浮雕效果**: 创建3D浮雕视觉效果

## 项目结构

```
project_filter/
├── convolution_demo.py    # 主程序文件
├── requirements.txt       # 依赖包列表
├── README.md              # 项目说明
└── images/
    └── xiaoren.png        # 示例图像
```

## 技术栈

- Python 3.x
- OpenCV (图像处理)
- Gradio (Web界面)
- NumPy (数值计算)
- Matplotlib (可视化)
