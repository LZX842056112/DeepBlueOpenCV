import cv2 as cv

# 测试图像加载
img = cv.imread('images/xiaoren.png')
if img is not None:
    print(f'图像加载成功: {img.shape}')
    print(f'图像尺寸: {img.shape[1]}x{img.shape[0]}')
    print(f'通道数: {img.shape[2] if len(img.shape) == 3 else 1}')
else:
    print('图像加载失败')
