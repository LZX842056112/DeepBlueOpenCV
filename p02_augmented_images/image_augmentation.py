import os
import cv2 as cv
import numpy as np
import gradio as gr
from pathlib import Path  # 用于处理文件路径
import random
from typing import List, Tuple


class ImageAugmentation:
    """图像数据增强
    用于计算机视觉任务中扩充训练数据集"""
    def __init__(self):
        self.images_dir = "images"                                  # 原始图片目录
        self.augmented_dir = "augmented_images"                     # 增强后图片保存目录
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp'}  # 支持的图片格式
        
        # 创建增强图片保存目录
        # exist_ok=True：目录不存在：创建目录；目录已存在：不报错，继续执行
        os.makedirs(self.augmented_dir, exist_ok=True)
    
    def load_images(self) -> List[str]:
        """从 images 目录加载所有图片路径"""
        image_paths = []
        # 扫描 images 目录
        # os.listdir(self.images_dir)：返回指定目录中所有文件的名称列表
        for file in os.listdir(self.images_dir):
            # 检查文件格式：将文件名转换为小写，检查文件名是否以指定的格式结尾 {'.jpg', '.jpeg', '.png', '.bmp'}
            # any()：如果生成器表达式中有任何一个为 True，就返回 True
            if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                # 构建完整路径并添加到列表
                image_paths.append(os.path.join(self.images_dir, file))
        # 返回所有支持的图片文件路径列表
        return image_paths
    
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """旋转图片"""
        # 图片高、宽、旋转中心
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        # 使用旋转矩阵实现任意角度旋转
        rotation_matrix = cv.getRotationMatrix2D(center, angle, 1.0)
        # 保持图片尺寸不变
        rotated = cv.warpAffine(image, rotation_matrix, (width, height))
        # 返回旋转后的图片
        return rotated
    
    def flip_image(self, image: np.ndarray, flip_code: int) -> np.ndarray:
        """翻转图片 (0=垂直, 1=水平, -1=双向)"""
        return cv.flip(image, flip_code)
    
    def adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        """调整亮度"""
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # 亮度调整：通过 HSV 色彩空间的 V 通道实现
        # cv.multiply()：对数组进行元素级乘法
        # factor：亮度调整因子
        hsv[:, :, 2] = cv.multiply(hsv[:, :, 2], factor)
        # 返回 BGR 格式的图片
        return cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    
    def adjust_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """调整对比度"""
        # 对图像进行线性变换来调整对比度，公式为：dst = |alpha × src + beta|
        # alpha：对比度因子，控制缩放比例
        # beta：亮度偏移量，这里设为 0 表示不改变亮度
        return cv.convertScaleAbs(image, alpha=factor, beta=0)
    
    def add_gaussian_noise(self, image: np.ndarray, mean: float = 0, std: float = 25) -> np.ndarray:
        """添加高斯噪声
        :param mean: 噪声的均值，默认为 0（正负噪声平衡）
        :param std: 噪声的标准差，默认为 25（控制噪声强度）"""
        # 生成符合高斯（正态）分布的随机数
        # image.shape: 生成与图像相同维度的噪声矩阵
        # .astype(np.uint8): 将噪声数据转换为 8 位无符号整数类型（0-255），与图像数据类型保持一致
        noise = np.random.normal(mean, std, image.shape).astype(np.uint8)
        # 添加噪声到图像
        # cv.add()自动处理溢出：200 + 100 = 255（不是 300）
        # 自动处理下溢：50 + (-100) = 0（不是 -50）
        noisy_image = cv.add(image, noise)
        return noisy_image
    
    def blur_image(self, image: np.ndarray, kernel_size: int) -> np.ndarray:
        """高斯模糊"""
        # 使用不同核大小进行模糊处理
        # (kernel_size, kernel_size)：高斯核的大小（宽度, 高度）
        # 0：高斯核在 X 和 Y 方向的标准差（sigma），0表示自动计算
        return cv.GaussianBlur(image, (kernel_size, kernel_size), 0)
    
    def sharpen_image(self, image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """锐化图片"""
        # 使用卷积核增强图像边缘和细节
        # 这是一个 3×3 的拉普拉斯锐化核（strength：强度）
        # 9 * strength：中心像素的权重
        kernel = np.array([[-1, -1, -1],
                          [-1, 9 * strength, -1],
                          [-1, -1, -1]])
        # 卷积操作
        # -1：输出图像深度（与输入相同），8位无符号整数 (CV_8U) ，每个通道取值范围：0-255
        # 图像深度（Image Depth）指的是存储每个像素所用的位数，它决定了图像可以表示的颜色数量
        return cv.filter2D(image, -1, kernel)
    
    def crop_image(self, image: np.ndarray, crop_ratio: float) -> np.ndarray:
        """随机裁剪图片
        随机选择裁剪区域，然后缩放到原图尺寸"""
        # 获取图像尺寸
        height, width = image.shape[:2]
        # 裁剪区域高度和宽度
        crop_height = int(height * crop_ratio)
        crop_width = int(width * crop_ratio)
        
        # 随机选择裁剪起始点
        start_y = random.randint(0, height - crop_height)
        start_x = random.randint(0, width - crop_width)

        # 从原图中提取矩形区域，尺寸：crop_height × crop_width
        cropped = image[start_y:start_y + crop_height, start_x:start_x + crop_width]
        # 将裁剪后的图像缩放回原图尺寸，保持输出图像尺寸一致
        return cv.resize(cropped, (width, height))
    
    def change_hue(self, image: np.ndarray, hue_shift: int) -> np.ndarray:
        """调整色调
        在 HSV 空间调整 H 通道"""
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # hsv[:, :, 0]：选择所有像素的 H 通道（色调）
        # + hue_shift：对每个像素的色调值进行偏移
        # % 180：取模运算，确保色调值在 0-179 范围内循环
        hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
        return cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    
    def change_saturation(self, image: np.ndarray, saturation_factor: float) -> np.ndarray:
        """调整饱和度
        在 HSV 空间调整 S 通道"""
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        # hsv[:, :, 1]：选择所有像素的 S 通道（饱和度）
        # cv2.multiply()：对饱和度值进行乘法运算
        # saturation_factor：饱和度调整因子
        hsv[:, :, 1] = cv.multiply(hsv[:, :, 1], saturation_factor)
        return cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    
    def perspective_transform(self, image: np.ndarray, strength: float) -> np.ndarray:
        """透视变换"""
        height, width = image.shape[:2]
        
        # 定义源点（原始图像的四个角）
        src_points = np.float32([[0, 0],                    # 左上角
                                 [width - 1, 0],            # 右上角
                                 [0, height - 1],           # 左下角
                                 [width - 1, height - 1]])  # 右下角
        
        # 计算目标点（变换后的四个角）
        # min(width, height)：取图像宽度和高度的较小值
        # strength：控制变换强度的参数
        # × 0.1：缩放因子，防止变换过于剧烈
        offset = int(min(width, height) * strength * 0.1)
        # 目标点坐标（仅仅是向中心缩小了图片）
        # TODO: 这里的透视变换过于简单，需要增加复杂度和随机性
        dst_points = np.float32([
            [offset, offset],                          # 左上角
            [width - 1 - offset, offset],              # 右上角
            [offset, height - 1 - offset],             # 左下角
            [width - 1 - offset, height - 1 - offset]  # 右下角
        ])
        
        # 计算透视变换矩阵
        # 计算从源点到目标点的 3×3 透视变换矩阵，这个矩阵描述了如何将图像从原始形状变换到新形状
        matrix = cv.getPerspectiveTransform(src_points, dst_points)
        # 应用透视变换
        transformed = cv.warpPerspective(image, matrix, (width, height))
        return transformed
    
    def apply_augmentation(self, image_path: str, augmentation_type: str, **kwargs) -> Tuple[np.ndarray, str]:
        """应用指定的增强方法
        :param image_path: 输入图像的文件路径
        :param augmentation_type: 增强类型名称（字符串）
        :param **kwargs: 可变关键字参数，用于传递各种增强方法的参数（将参数打包成字典给函数体调用）
        :返回值: 元组 (增强后的图像, 保存路径)"""
        # 加载图像
        image = cv.imread(image_path)
        # 检查图像是否成功加载
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 创建图像副本用于增强处理
        augmented = image.copy()
        
        # 根据指定的增强类型应用相应的增强处理，每种都有可调节的参数
        if augmentation_type == "rotate":                             # 旋转
            angle = kwargs.get('angle', 30)                           # 默认 30 度
            augmented = self.rotate_image(image, angle)
        elif augmentation_type == "flip_horizontal":                  # 水平翻转
            augmented = self.flip_image(image, 1)
        elif augmentation_type == "flip_vertical":                    # 垂直翻转
            augmented = self.flip_image(image, 0)
        elif augmentation_type == "brightness":                       # 亮度
            factor = kwargs.get('factor', 1.5)                        # 默认亮度因子 1.5
            augmented = self.adjust_brightness(image, factor)
        elif augmentation_type == "contrast":                         # 对比度
            factor = kwargs.get('factor', 1.5)                        # 默认对比度因子 1.5
            augmented = self.adjust_contrast(image, factor)
        elif augmentation_type == "gaussian_noise":                   # 高斯噪声
            augmented = self.add_gaussian_noise(image)
        elif augmentation_type == "blur":                             # 高斯模糊
            kernel_size = kwargs.get('kernel_size', 5)                # 默认核大小 5
            augmented = self.blur_image(image, kernel_size)
        elif augmentation_type == "sharpen":                          # 锐化
            strength = kwargs.get('strength', 1.0)                    # 默认锐化强度 1.0
            augmented = self.sharpen_image(image, strength)
        elif augmentation_type == "crop":                             # 裁剪
            crop_ratio = kwargs.get('crop_ratio', 0.8)                # 默认裁剪比例 0.8
            augmented = self.crop_image(image, crop_ratio)
        elif augmentation_type == "hue_shift":                        # 色调
            hue_shift = kwargs.get('hue_shift', 30)                   # 默认色调偏移 30
            augmented = self.change_hue(image, hue_shift)
        elif augmentation_type == "saturation":                       # 饱和度
            saturation_factor = kwargs.get('saturation_factor', 1.5)  # 默认饱和度因子 1.5
            augmented = self.change_saturation(image, saturation_factor)
        elif augmentation_type == "perspective":                      # 透视变换
            strength = kwargs.get('strength', 0.5)                    # 默认透视强度 0.5
            augmented = self.perspective_transform(image, strength)
        else:
            raise ValueError(f"不支持的增强类型: {augmentation_type}")
        
        # 生成保存路径
        # 获取文件名（不含扩展名）
        filename = Path(image_path).stem
        # 增强类型
        aug_type = augmentation_type
        # 保存到 augmented_images 目录，格式：原文件名_增强类型.jpg
        save_path = os.path.join(self.augmented_dir, f"{filename}_{aug_type}.jpg")
        
        # 返回增强后的图像和保存路径
        return augmented, save_path
    
    def save_image(self, image: np.ndarray, save_path: str):
        """保存图片"""
        # 将增强的图片保存到 augmented_images 目录
        cv.imwrite(save_path, image)


def create_gradio_interface():
    """创建 Gradio 界面"""
    # 创建增强器实例
    aug = ImageAugmentation()
    
    def process_single_image(
            image_path: str,          # 图片路径
            augmentation_type: str,   # 增强类型
            angle=30,                 # 旋转角度
            brightness_factor=1.5,    # 亮度因子
            contrast_factor=1.5,      # 对比度因子
            blur_kernel=5,            # 高斯模糊核大小
            sharpen_strength=1.0,     # 锐化强度
            crop_ratio=0.8,           # 裁剪比例
            hue_shift=30,             # 色调偏移
            saturation_factor=1.5,    # 饱和度因子
            perspective_strength=0.5  # 透视强度
    ):
        """处理单张图片"""
        try:
            # 根据用户选择的增强类型，只传递相关的参数到增强器 {'angle': 30}
            kwargs = {}
            if augmentation_type == "rotate":         # 旋转
                kwargs['angle'] = angle
            elif augmentation_type == "brightness":   # 亮度
                kwargs['factor'] = brightness_factor
            elif augmentation_type == "contrast":     # 对比度
                kwargs['factor'] = contrast_factor
            elif augmentation_type == "blur":         # 高斯模糊
                kwargs['kernel_size'] = blur_kernel
            elif augmentation_type == "sharpen":      # 锐化
                kwargs['strength'] = sharpen_strength
            elif augmentation_type == "crop":         # 裁剪
                kwargs['crop_ratio'] = crop_ratio
            elif augmentation_type == "hue_shift":    # 色调
                kwargs['hue_shift'] = hue_shift
            elif augmentation_type == "saturation":   # 饱和度
                kwargs['saturation_factor'] = saturation_factor
            elif augmentation_type == "perspective":  # 透视
                kwargs['strength'] = perspective_strength

            # 调用增强器进行图像处理，返回增强后的图像、保存路径
            # **kwargs：在字典对象前面加双星（**），使其以关键字参数的形式传入函数
            # {'angle': 30} -> (image_path, augmentation_type, angle=30)
            augmented_img, save_path = aug.apply_augmentation(image_path, augmentation_type, **kwargs)
            # 调用增强器保存增强后的图片
            aug.save_image(augmented_img, save_path)
            
            # 将增强后的图片转换为 RGB 格式用于显示
            augmented_rgb = cv.cvtColor(augmented_img, cv.COLOR_BGR2RGB)
            # 将原始图片转换为 RGB 格式用于显示
            original_rgb = cv.cvtColor(cv.imread(image_path), cv.COLOR_BGR2RGB)
            
            # 返回原图、增强图和结果信息
            return original_rgb, augmented_rgb, f"增强完成！保存至: {save_path}"
        except Exception as e:
            # 返回 None, None, 错误信息 三元组
            return None, None, f"处理失败: {str(e)}"
    
    def batch_augment(augmentation_type: str, num_augmentations: int, **kwargs):
        """批量增强所有图片
        :param augmentation_type: 增强类型
        :param num_augmentations: 每张图片生成的增强版本数量
        :param **kwargs: 其他可选参数"""
        try:
            # 从 images 目录加载所有支持的图片
            image_paths = aug.load_images()
            # 如果没有找到图片，立即返回提示信息
            if not image_paths:
                return "未找到任何图片！"
            
            # 初始化结果记录，用于记录每个生成图片的保存路径
            results = []
            # 遍历目录中的每张原始图片
            for img_path in image_paths:
                # 为每张原始图片生成指定数量的增强版本
                for i in range(num_augmentations):
                    # 对于某些增强方法，添加随机参数
                    if augmentation_type == "rotate":        # 旋转
                        kwargs['angle'] = random.randint(-180, 180)
                    elif augmentation_type == "brightness":  # 亮度
                        kwargs['factor'] = random.uniform(0.5, 2.0)
                    elif augmentation_type == "contrast":    # 对比度
                        kwargs['factor'] = random.uniform(0.5, 2.0)
                    elif augmentation_type == "crop":        # 裁剪
                        kwargs['crop_ratio'] = random.uniform(0.7, 0.95)
                    elif augmentation_type == "hue_shift":   # 色调
                        kwargs['hue_shift'] = random.randint(-30, 30)
                    elif augmentation_type == "saturation":  # 饱和度
                        kwargs['saturation_factor'] = random.uniform(0.5, 2.0)
                    
                    # 调用增强器应用指定的增强方法
                    augmented_img, save_path = aug.apply_augmentation(img_path, augmentation_type, **kwargs)
                    # 自动保存增强后的图片
                    aug.save_image(augmented_img, save_path)
                    # 记录生成的文件路径
                    results.append(f"生成: {save_path}")
            
            # 结果汇总和返回
            # - 总生成数量统计
            # - 显示前 10 个生成文件的路径
            # - 如果超过 10 个，用"..."省略
            # TODO: 设置每张图片生成数量为 3，结果 3 个图片文件重名，只保存了 1 个，需要存为 3 个不同的文件名
            return f"批量增强完成！共生成 {len(results)} 张图片\n" + "\n".join(results[:10]) + ("\n..." if len(results) > 10 else "")
        except Exception as e:
            return f"批量增强失败: {str(e)}"
    
    # 创建界面
    with gr.Blocks(title="图片增强工具 - 深度学习数据增强") as demo:
        gr.Markdown("# 🖼️ 图片增强工具")
        gr.Markdown("用于深度学习模型训练时的数据增强")
        
        with gr.Tab("单张图片增强"):
            with gr.Row():
                # 左侧：输入控制区
                with gr.Column():
                    # 各种输入控件
                    # 图片选择器
                    image_selector = gr.Dropdown(
                        choices=aug.load_images(),                                 # 动态加载图片列表
                        label="选择图片",
                        value=aug.load_images()[0] if aug.load_images() else None  # 默认选择第一张
                    )

                    # 增强类型选择
                    # TODO: 将增强类型改为中文
                    augmentation_type = gr.Dropdown(
                        choices=[  # 所有支持的增强类型
                            "rotate", "flip_horizontal", "flip_vertical", 
                            "brightness", "contrast", "gaussian_noise",
                            "blur", "sharpen", "crop", "hue_shift",
                            "saturation", "perspective"
                        ],
                        label="增强类型",
                        value="rotate"  # 默认选择旋转
                    )

                    # 高级参数区域（可折叠）
                    with gr.Accordion("高级参数", open=False):  # 默认折叠
                        # 参数滑块说明
                        # gr.Slider(min, max, value, label, visible)
                        # 每个增强类型有对应的参数范围，初始时只显示旋转角度的滑块
                        angle_slider = gr.Slider(-180, 180, value=30, label="旋转角度", visible=True)
                        brightness_slider = gr.Slider(0.1, 3.0, value=1.5, label="亮度因子", visible=False)
                        contrast_slider = gr.Slider(0.1, 3.0, value=1.5, label="对比度因子", visible=False)
                        blur_slider = gr.Slider(3, 15, value=5, step=2, label="模糊核大小", visible=False)
                        sharpen_slider = gr.Slider(0.1, 3.0, value=1.0, label="锐化强度", visible=False)
                        crop_slider = gr.Slider(0.5, 0.95, value=0.8, label="裁剪比例", visible=False)
                        hue_slider = gr.Slider(-90, 90, value=30, label="色调偏移", visible=False)
                        saturation_slider = gr.Slider(0.1, 3.0, value=1.5, label="饱和度因子", visible=False)
                        perspective_slider = gr.Slider(0.1, 1.0, value=0.5, label="透视强度", visible=False)
                    
                    # 处理按钮（显示为主要按钮样式）
                    process_btn = gr.Button("应用增强", variant="primary")

                # 右侧：结果显示区
                with gr.Column():
                    # 显示组件
                    # 显示原始和增强后的图片对比
                    # interactive=False：组件是只读的
                    original_image = gr.Image(label="原始图片", interactive=False)
                    augmented_image = gr.Image(label="增强后图片", interactive=False)
                    # 显示处理状态和结果信息
                    result_text = gr.Textbox(label="处理结果", interactive=False)
        
        with gr.Tab("批量增强"):
            with gr.Row():
                # 左侧：输入控制区
                with gr.Column():
                    # 批量增强类型选择
                    # TODO: 将批量增强类型改为中文
                    batch_aug_type = gr.Dropdown(
                        choices=[
                            "rotate", "flip_horizontal", "flip_vertical", 
                            "brightness", "contrast", "gaussian_noise",
                            "blur", "sharpen", "crop", "hue_shift",
                            "saturation", "perspective"
                        ],
                        label="增强类型",
                        value="rotate"
                    )
                    # 每张图片可以生成多个增强版本（1-10个），默认为 3
                    num_augmentations = gr.Slider(1, 10, value=3, step=1, label="每张图片生成数量")
                    batch_process_btn = gr.Button("批量增强", variant="primary")

                # 右侧：结果显示区
                with gr.Column():
                    # 结果显示在多行文本框中
                    batch_result = gr.Textbox(label="批量处理结果", lines=10)

        def toggle_parameters(aug_type):
            """动态显示/隐藏参数控件
            :aug_type: 增强类型字符串"""
            # 增强类型的可见性配置
            visibility = {
                "rotate": [True, False, False, False, False, False, False, False, False],      # 旋转
                "brightness": [False, True, False, False, False, False, False, False, False],  # 亮度
                "contrast": [False, False, True, False, False, False, False, False, False],    # 对比度
                "blur": [False, False, False, True, False, False, False, False, False],        # 模糊
                "sharpen": [False, False, False, False, True, False, False, False, False],     # 锐化
                "crop": [False, False, False, False, False, True, False, False, False],        # 裁剪
                "hue_shift": [False, False, False, False, False, False, True, False, False],   # 色调
                "saturation": [False, False, False, False, False, False, False, True, False],  # 饱和度
                "perspective": [False, False, False, False, False, False, False, False, True]  # 透视
            }
            
            # 全部隐藏
            default_visibility = [False] * 9
            # 如果 aug_type 在字典中，返回对应的可见性列表；如果不在字典中，返回全 False 的默认列表
            vis = visibility.get(aug_type, default_visibility)

            # 返回 9 个滑块的可见性状态列表
            # NOTE：这里返回的是新的控件实例，Gradio 会用它来更新界面
            return [
                gr.Slider(visible=vis[0]),  # 旋转角度滑块 [True, False, False, False, False, False, False, False, False]
                gr.Slider(visible=vis[1]),  # 亮度因子滑块
                gr.Slider(visible=vis[2]),  # 对比度因子滑块
                gr.Slider(visible=vis[3]),  # 模糊核大小滑块
                gr.Slider(visible=vis[4]),  # 锐化强度滑块
                gr.Slider(visible=vis[5]),  # 裁剪比例滑块
                gr.Slider(visible=vis[6]),  # 色调偏移滑块
                gr.Slider(visible=vis[7]),  # 饱和度因子滑块
                gr.Slider(visible=vis[8])   # 透视强度滑块
            ]
        
        # 单张图片处理
        # 输入数据：从界面控件获取
        # 输出更新：更新结果显示区域
        process_btn.click(
            fn=process_single_image,  # 处理单张图片函数，返回原图、增强图和结果信息
            inputs=[
                image_selector,       # 图片选择器
                augmentation_type,    # 增强类型下拉框的选择值
                angle_slider,         # 旋转角度滑块
                brightness_slider,    # 亮度因子滑块
                contrast_slider,      # 对比度因子滑块
                blur_slider,          # 模糊核大小滑块
                sharpen_slider,       # 锐化强度滑块
                crop_slider,          # 裁剪比例滑块
                hue_slider,           # 色调偏移滑块
                saturation_slider,    # 饱和度因子滑块
                perspective_slider    # 透视强度滑块
            ],
            outputs=[
                original_image,       # 原始图片
                augmented_image,      # 增强后图片
                result_text           # 处理结果
            ]
        )
        
        # 批量处理
        batch_process_btn.click(
            fn=batch_augment,      # 批量增强所有图片函数，返回结果汇总
            inputs=[
                batch_aug_type,    # 批量增强类型下拉框的选择值
                num_augmentations  # 生成数量滑块的值
            ],
            outputs=batch_result   # 更新这个文本框，显示批量处理的结果信息，包括生成的文件列表和统计信息
        )
        
        # 参数可见性切换
        augmentation_type.change(
            fn=toggle_parameters,      # 动态显示/隐藏参数控件（函数），返回 [True, False, False, False, False, False, False, False, False]
            inputs=augmentation_type,  # 增强类型下拉框的选择值
            outputs=[                  # 所有参数滑块的选择值
                angle_slider, brightness_slider, contrast_slider,
                blur_slider, sharpen_slider, crop_slider,
                hue_slider, saturation_slider, perspective_slider
            ]
        )

        # 更新图片选择下拉框的选项列表
        def refresh_images():
            # aug.load_images()：从磁盘重新加载，返回所有支持的图片文件路径列表
            return gr.Dropdown(choices=aug.load_images())
        
        # 界面加载时自动刷新，确保显示最新的图片文件
        demo.load(
            fn=refresh_images,      # 刷新图片列表函数
            outputs=image_selector  # 使用返回的新下拉框更新图片选择器
        )
    
    # 返回构建好的界面对象
    return demo


if __name__ == "__main__":
    # 调用 create_gradio_interface() 函数，返回配置好的 demo 对象
    demo = create_gradio_interface()
    # 启动 Gradio 应用
    demo.launch(
        share=True,                 # 本地开发时通常设为 False，生产分享时设为 True
        server_name="0.0.0.0",      # 本机 + 局域网内其他设备都可以访问
        server_port=7867,           # 指定端口
        prevent_thread_lock=False,  # 程序阻塞，直到服务停止，适用于独立应用
    )
    print("这行代码永远不会执行")      # 因为程序在 launch() 处阻塞
