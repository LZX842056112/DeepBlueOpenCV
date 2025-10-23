"""
这是一个基于 Gradio 的卷积操作可视化演示程序，用于展示不同卷积核对图像的处理效果
"""
import cv2 as cv
import numpy as np
import gradio as gr
from typing import Tuple, List
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# 设置字符集，防止中文乱码
plt.rcParams["font.sans-serif"] = [u"simHei"]
plt.rcParams["axes.unicode_minus"] = False


class ConvolutionDemo:
    """卷积操作演示"""
    def __init__(self):
        self.image_path = "images/xiaoren.png"  # 设置默认图像路径
        self.original_image = None              # 初始化图像变量为 None
        self.load_image()                       # 调用 load_image()方法加载图像
        
    def load_image(self):
        """加载并预处理图像"""
        try:
            # 读取图像文件
            self.original_image = cv.imread(self.image_path)
            # cv.imread()在文件不存在时会返回 None 而不是抛出异常
            if self.original_image is None:
                # 手动抛出异常
                raise FileNotFoundError(f"无法加载图像: {self.image_path}")
            # 转换为 RGB 格式用于显示，例如 matplotlib
            self.original_image_rgb = cv.cvtColor(self.original_image, cv.COLOR_BGR2RGB)
        except Exception as e:
            print(f"加载图像时出错: {e}")
            # 创建灰色备用图像（即使图像加载失败，程序也能继续运行）
            # np.ones((300, 300, 3), dtype=np.uint8)：创建白色图像
            # * 128：将像素值设为 128，创建中灰色图像
            self.original_image = np.ones((300, 300, 3), dtype=np.uint8) * 128
            # 创建副本确保两个图像变量都有值
            self.original_image_rgb = self.original_image.copy()
    
    def apply_convolution(self, kernel_type: str, kernel_size: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """应用指定的卷积核
        输入：卷积核类型（字符串）和大小（默认 3×3）
        输出：元组，包含处理后的 RGB 图像、使用的卷积核
        返回类型：两个 numpy 数组"""
        # 确保图像已加载
        if self.original_image is None:
            self.load_image()
            
        # 转换为灰度图像用于卷积操作
        # 简化卷积计算（单通道 vs 三通道），大多数图像处理算法在灰度图上效果更明显
        gray_image = cv.cvtColor(self.original_image, cv.COLOR_BGR2GRAY)
        
        # 定义不同的卷积核
        # 使用字典映射卷积核名称到具体的核方法，部分卷积核接受 kernel_size 参数
        kernels = {
            "identity": self.get_identity_kernel(kernel_size),
            "blur": self.get_blur_kernel(kernel_size),
            "gaussian_blur": self.get_gaussian_blur_kernel(kernel_size),
            "sharpen": self.get_sharpen_kernel(),
            "edge_detection": self.get_edge_detection_kernel(),
            "sobel_x": self.get_sobel_x_kernel(),
            "sobel_y": self.get_sobel_y_kernel(),
            "laplacian": self.get_laplacian_kernel(),
            "emboss": self.get_emboss_kernel()
        }
        
        # 卷积核选择
        # 安全获取：使用 get() 方法，提供默认值
        # 如果输入无效的 kernel_type，默认使用单位卷积核
        kernel = kernels.get(kernel_type, kernels["identity"])
        
        # 应用卷积
        if kernel_type in ["sobel_x", "sobel_y", "laplacian", "edge_detection"]:
            # 边缘检测类：这些核可能产生负值，需要特殊处理
            # 这些卷积核包含负权重，计算结果可能为负
            # .astype(np.float32)：uint8无法表示负数，需要先转为 float32
            # -1：表示输出与输入相同深度
            filtered_image = cv.filter2D(gray_image.astype(np.float32), -1, kernel)
            # 取绝对值（边缘强度）
            filtered_image = np.abs(filtered_image)
            # 归一化：需要将结果映射到 0-255 范围便于显示
            filtered_image = cv.normalize(filtered_image, None, 0, 255, cv.NORM_MINMAX)
            # 转回 8 位无符号整数
            filtered_image = filtered_image.astype(np.uint8)
        else:
            # 普通卷积核处理
            # 对于模糊、锐化等核，结果通常在 0-255 范围内，不需要数据类型转换和归一化
            filtered_image = cv.filter2D(gray_image, -1, kernel)
        
        # 将灰度结果转换为 RGB 用于显示（与原始彩色图像显示格式统一）
        filtered_image_rgb = cv.cvtColor(filtered_image, cv.COLOR_GRAY2RGB)
        
        # 返回元组，包含处理后的 RGB 图像、使用的卷积核
        return filtered_image_rgb, kernel
    
    def get_identity_kernel(self, size: int) -> np.ndarray:
        """单位卷积核
        保持原图像不变
        [[0, 0, 0],
         [0, 1, 0],
         [0, 0, 0]]"""
        kernel = np.zeros((size, size))
        # 中心位置设为 1
        kernel[size // 2, size // 2] = 1
        return kernel
    
    def get_blur_kernel(self, size: int) -> np.ndarray:
        """均值模糊卷积核
        每个输出像素是周围 size×size 区域内像素的平均值
        [[1/9, 1/9, 1/9],
         [1/9, 1/9, 1/9],
         [1/9, 1/9, 1/9]]"""
        # 归一化，确保所有权重之和为 1
        return np.ones((size, size)) / (size * size)
    
    def get_gaussian_blur_kernel(self, size: int) -> np.ndarray:
        """高斯模糊卷积核
        更自然的模糊效果，保留更多边缘信息
        [[0.02, 0.08, 0.02],
         [0.08, 0.64, 0.08],
         [0.02, 0.08, 0.02]]"""
        kernel = np.zeros((size, size))
        # 中心的位置
        center = size // 2
        # 根据卷积核大小动态计算标准差 σ，σ与卷积核大小成正比
        sigma = 0.3 * ((size - 1) * 0.5 - 1) + 0.8

        # 使用二维高斯函数计算每个位置的权重（距离中心越远，权重越小）
        for i in range(size):
            for j in range(size):
                x = i - center  # x方向距离中心的位置
                y = j - center  # y方向距离中心的位置
                # 计算未归一化的高斯权重
                kernel[i, j] = np.exp(-(x ** 2 + y ** 2) / (2 * sigma ** 2))
        
        # 归一化：确保所有权重之和为 1，保持图像整体亮度不变
        # np.sum(kernel)：高斯函数离散化后的近似积分值，近似于但不等于2πσ²
        return kernel / np.sum(kernel)
    
    def get_sharpen_kernel(self) -> np.ndarray:
        """锐化卷积核
        通过增强中心像素与周围像素的差异，来增强图像边缘和纹理细节，使图像看起来更清晰
        """
        # 中心权重：5（增强中心像素）
        # 周围权重：-1（减弱相邻像素）
        # 净权重和：5 + 4×(-1) = 1（保持整体亮度）
        return np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
    
    def get_edge_detection_kernel(self) -> np.ndarray:
        """边缘检测卷积核
        这是拉普拉斯算子的一种形式，检测像素值的二阶导数变化
        在平坦区域输出接近 0，在边缘处输出较大值"""
        # 中心权重：8（强烈增强中心）
        # 周围权重：-1（强烈减弱周围）
        # 净权重和：8 + 8×(-1) = 0（零和核）
        return np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ])
    
    def get_sobel_x_kernel(self) -> np.ndarray:
        """Sobel X方向卷积核
        计算图像在水平方向的近似导数
        水平方向梯度：检测从左到右的亮度变化"""
        # 中心列权重：0（忽略垂直方向的像素）
        # 左右不对称：左侧负权重，右侧正权重
        # 净权重和：0（零和核）
        return np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ])
    
    def get_sobel_y_kernel(self) -> np.ndarray:
        """Sobel Y方向卷积核
        计算图像在垂直方向的近似导数
        垂直方向梯度：检测从上到下的亮度变化"""
        return np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ])
    
    def get_laplacian_kernel(self) -> np.ndarray:
        """拉普拉斯卷积核
        这是离散拉普拉斯算子的标准形式
        计算像素在四个方向（上、下、左、右）的二阶导数
        检测所有方向的边缘，对噪声敏感
        输出图像中：
        平坦区域：接近 0（灰色）
        边缘区域：高正值或低负值"""
        # 中心权重：-4（强烈减弱中心像素）
        # 相邻权重：1（增强直接相邻像素）
        # 对角权重：0（忽略对角像素）
        # 净权重和：0（零和核）
        return np.array([
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ])
    
    def get_emboss_kernel(self) -> np.ndarray:
        """浮雕卷积核
        创建三维浮雕效果
        左上方向边缘显示为暗色（背光面）
        右下方向边缘显示为亮色（受光面）
        平坦区域变为中灰色"""
        # 不对称权重：从左上到右下逐渐增加
        # 模拟光照：假设光源来自左上角
        # 净权重和：1（-2-1+0-1+1+1+0+1+2 = 1）
        return np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ])
    
    def visualize_kernel(self, kernel: np.ndarray) -> Figure:
        """可视化卷积核
        创建卷积核的热力图，显示具体数值
        输入：卷积核矩阵（numpy 数组）
        输出：matplotlib图形对象"""
        # 创建图形和坐标轴对象
        fig, ax = plt.subplots(figsize=(4, 4))
        # 绘制热力图
        # ax.imshow()：将矩阵显示为图像
        # cmap='coolwarm'：使用"冷热"颜色映射
        # interpolation='nearest'：禁用插值，保持像素块的清晰边界
        im = ax.imshow(kernel, cmap='coolwarm', interpolation='nearest')
        
        # 显示数值
        # 遍历行
        for i in range(kernel.shape[0]):
            # 遍历列
            for j in range(kernel.shape[1]):
                # f'{kernel[i, j]:.2f}'：格式化数值，保留 2 位小数
                ax.text(j, i, f'{kernel[i, j]:.2f}',
                        # 水平和垂直居中对齐
                        ha='center', va='center',
                        # 绝对值大于 0.5 时用白色文字，否则用黑色文字
                        color='white' if abs(kernel[i, j]) > 0.5 else 'black',
                        fontsize=8)

        # 设置图形标题
        ax.set_title('卷积核矩阵')
        # 显示网格线
        ax.set_xticks(range(kernel.shape[1]))
        ax.set_yticks(range(kernel.shape[0]))
        # 在图形旁边添加颜色条，显示数值与颜色的对应关系
        # im：是之前 imshow() 返回的图像对象
        # ax=ax：指定颜色条属于哪个坐标轴
        plt.colorbar(im, ax=ax)
        # 自动调整子图参数，避免标签重叠
        plt.tight_layout()
        # 返回 fig 对象供 Gradio 界面显示
        return fig


def create_interface():
    """创建 Gradio 界面"""
    # 创建 ConvolutionDemo 类的实例，用于处理图像和卷积操作
    demo = ConvolutionDemo()
    
    def process_image(kernel_type: str, kernel_size: int):
        """处理图像并返回结果"""
        # 应用卷积核，得到处理后的图像、卷积核
        filtered_image, kernel = demo.apply_convolution(kernel_type, kernel_size)
        # 可视化卷积核矩阵
        kernel_fig = demo.visualize_kernel(kernel)
        
        # 返回原始图像、处理后的图像、卷积核图
        return demo.original_image_rgb, filtered_image, kernel_fig
    
    # 定义卷积核类型选项
    kernel_types = [
        "identity", "blur", "gaussian_blur", "sharpen", 
        "edge_detection", "sobel_x", "sobel_y", "laplacian", 
        "emboss"
    ]

    # 卷积核描述字典
    kernel_descriptions = {
        "identity": "单位卷积核 - 不改变图像",
        "blur": "均值模糊 - 平滑图像",
        "gaussian_blur": "高斯模糊 - 更自然的平滑效果",
        "sharpen": "锐化 - 增强图像细节",
        "edge_detection": "边缘检测 - 突出显示边缘",
        "sobel_x": "Sobel X方向 - 水平边缘检测",
        "sobel_y": "Sobel Y方向 - 垂直边缘检测", 
        "laplacian": "拉普拉斯 - 二阶导数边缘检测",
        "emboss": "浮雕效果 - 创建3D浮雕效果"
    }
    
    # 界面布局构建
    with gr.Blocks(title="卷积操作可视化演示", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🎨 卷积操作可视化演示")
        gr.Markdown("使用不同的卷积核处理图像，观察效果变化")

        # 控制面板布局（第一行）
        with gr.Row():
            # 左侧控制列
            with gr.Column():
                # 卷积核类型下拉选择
                kernel_choice = gr.Dropdown(
                    choices=kernel_types,
                    value="identity",  # 默认值
                    label="选择卷积核类型",
                    info="选择要应用的卷积操作"
                )

                # 卷积核大小滑块
                kernel_size = gr.Slider(
                    minimum=3,
                    maximum=15,
                    value=3,  # 默认值
                    step=2,   # 步长
                    label="卷积核大小",
                    info="只对支持大小变化的卷积核有效"
                )

                # 处理按钮
                process_btn = gr.Button("应用卷积", variant="primary")
                
                # 描述文本框
                description_box = gr.Textbox(
                    label="卷积核描述",
                    value=kernel_descriptions["identity"],
                    interactive=False  # 只读
                )

            # 右侧可视化列
            with gr.Column():
                gr.Markdown("### 卷积核可视化")
                kernel_plot = gr.Plot(label="卷积核矩阵")
        
        # 图像显示布局（第二行）
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 原始图像")
                original_image = gr.Image(label="原始图像", interactive=False)
            
            with gr.Column():
                gr.Markdown("### 处理后的图像")
                filtered_image = gr.Image(label="处理后图像", interactive=False)
        
        # 动态更新描述
        def update_description(kernel_type):
            # 当用户选择不同的卷积核时，自动更新描述文本
            return kernel_descriptions.get(kernel_type, "未知卷积核")
        
        # change 事件监听下拉选择的变化
        kernel_choice.change(
            update_description,        # 函数：动态更新描述
            inputs=[kernel_choice],    # 当前选择的 kernel_type 卷积核类型字符串
            outputs=[description_box]  # description_box 描述文本框的内容
        )
        
        # 处理按钮点击事件（点击"应用卷积"按钮时触发）
        process_btn.click(
            process_image,                                         # 函数：处理图像
            inputs=[kernel_choice, kernel_size],                   # 当前选择的卷积核类型和大小
            # 更新三个显示区域：原始 RGB 图像、卷积处理后的图像、卷积核矩阵可视化
            outputs=[original_image, filtered_image, kernel_plot]
        )
        
        # 初始化显示
        interface.load(
            # 界面加载时执行匿名函数，自动显示默认结果（单位卷积核，3×3大小）
            lambda: process_image("identity", 3),
            # 更新三个显示区域：原始 RGB 图像、卷积处理后的图像、卷积核矩阵可视化
            outputs=[original_image, filtered_image, kernel_plot]
        )
    
    # 返回界面布局
    return interface


if __name__ == "__main__":
    # 创建并启动界面
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",  # 监听所有可用的网络接口
        server_port=7861,       # 端口号
        share=False,            # 不创建公共链接，仅局域网访问
        inbrowser=True          # 服务器启动后自动打开默认浏览器
    )
