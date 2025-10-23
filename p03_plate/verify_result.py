"""
这是一个输出结果验证系统，用于检查透视变换后的车牌图像质量
"""
import cv2 as cv
import numpy as np


def verify_output():
    """
    验证输出图片是否符合要求
    """
    output_path = "output/transformed_plate.jpg"
    
    # 读取输出图片
    image = cv.imread(output_path)
    if image is None:
        print(f"无法读取输出图片: {output_path}")
        return False
    
    height, width = image.shape[:2]
    
    print(f"输出图片尺寸: {width}x{height} 像素")
    print(f"要求尺寸: 314x100 像素")
    
    # 检查尺寸是否符合要求
    if width == 314 and height == 100:
        print("[OK] 尺寸符合要求")
        
        # 检查是否包含黑色区域
        # 将图片转换为灰度
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        
        # 统计黑色像素数量（灰度值小于 10）
        black_pixels = np.sum(gray < 10)
        total_pixels = width * height
        
        black_percentage = (black_pixels / total_pixels) * 100
        print(f"黑色像素比例: {black_percentage:.2f}%")

        # 如果黑色像素少于 5%，认为基本没有黑色区域
        if black_percentage < 5:
            print("[OK] 基本没有黑色区域")
        else:
            print("[WARNING] 包含较多黑色区域")
        
        return True
    else:
        print("[ERROR] 尺寸不符合要求")
        return False


def check_blue_content():
    """
    检查蓝色内容
    """
    output_path = "output/transformed_plate.jpg"
    image = cv.imread(output_path)
    
    if image is None:
        return
    
    # 转换到 HSV 颜色空间
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # 定义蓝色范围
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([140, 255, 255])
    
    # 创建蓝色掩码
    blue_mask = cv.inRange(hsv, lower_blue, upper_blue)
    
    # 统计蓝色像素
    blue_pixels = np.sum(blue_mask > 0)
    total_pixels = image.shape[0] * image.shape[1]
    
    blue_percentage = (blue_pixels / total_pixels) * 100
    print(f"蓝色像素比例: {blue_percentage:.2f}%")
    
    if blue_percentage > 30:
        print("[OK] 包含显著的蓝色区域")
    else:
        print("[WARNING] 蓝色区域较少")


if __name__ == "__main__":
    print("验证输出结果...")
    print("-" * 40)
    
    success = verify_output()
    
    if success:
        print("\n检查蓝色内容...")
        print("-" * 40)
        check_blue_content()
        
        print("\n" + "=" * 40)
        print("验证完成！")
    else:
        print("\n验证失败，请检查处理过程。")
