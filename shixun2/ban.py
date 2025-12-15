import cv2
import numpy as np
import os
import time
import matplotlib.pyplot as plt


def detect_brown_defects_single_box(img, mask, min_area=20):
    """
    在前景区域内检测褐色斑点，并只标出最大的那个缺陷的红框。
    :param img: 原始 BGR 图像 (会被直接修改)
    :param mask: GrabCut 生成的二值掩膜
    :param min_area: 最小缺陷面积阈值
    """
    # 转换为 HSV 颜色空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义褐色的 HSV 阈值 (根据实际情况微调)
    # 色调偏红橙(0-30), 饱和度中等到高(40-255), 亮度中等到低(20-200)
    lower_brown = np.array([0, 40, 20])
    upper_brown = np.array([30, 255, 200])

    # 创建二值掩膜，褐色区域为白色(255)，其他为黑色(0)。
    color_mask = cv2.inRange(hsv, lower_brown, upper_brown)

    # 结合 GrabCut 的掩膜
    # 将0/1掩膜转换为0/255
    mask_visual = (mask * 255).astype(np.uint8)
    # 逻辑与操作，只在管子区域(前景)检测褐色
    final_mask = cv2.bitwise_and(color_mask, mask_visual)

    # 使用3×3核的开运算（先腐蚀后膨胀）去除小噪声点
    kernel = np.ones((3, 3), np.uint8)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)

    # 查找轮廓
    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 记录最大面积
    max_area = 0
    # 记录最大缺陷的边界框
    best_rect = None
    # 标记是否找到任何符合条件的缺陷
    found_any = False

    # 遍历所有检测到的轮廓，找出最大的那个
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            found_any = True
            # 如果当前这个比之前记录的都大，就更新最大值
            if area > max_area:
                max_area = area
                best_rect = cv2.boundingRect(cnt)

    # 循环结束后，如果找到了最大的缺陷，只画这一个框
    if best_rect is not None:
        x, y, w, h = best_rect
        pad = 5  # 外扩一点像素，让框不那么紧贴
        # 画红框 (BGR: 0, 0, 255), 线宽 3
        # 使用 max(0, ...) 防止坐标超出图像边界
        cv2.rectangle(img, (max(0, x - pad), max(0, y - pad)),
                      (x + w + pad, y + h + pad), (0, 0, 255), 3)
        print(f"  -> 已标记最大的缺陷: 面积 {max_area:.1f}, 位置 ({x},{y})")
    elif found_any:
        print(f"  -> 检测到疑似缺陷，但面积均小于阈值 {min_area}，忽略。")



def remove_background_grabcut_fast(image_path, scale_factor, iter_count):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    # 降采样，按比例缩小图像加速处理
    small_w = int(w * scale_factor)
    small_h = int(h * scale_factor)
    # 防止尺寸过小
    if small_w < 10 or small_h < 10: small_w, small_h = w, h
    small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_AREA)

    # 定义初始的前景矩形区域（左20%，上5%，右60%，下90%）
    rect_small = (int(small_w * 0.2), int(small_h * 0.05), int(small_w * 0.6), int(small_h * 0.9))
    # 初始化掩膜和GrabCut算法使用的背景/前景模型
    mask_small = np.zeros(small_img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # 执行GrabCut算法分割前景和背景
    try:
        cv2.grabCut(small_img, mask_small, rect_small, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

    # 将GrabCut结果转换为二值掩膜（0=背景，1=前景）
    mask2_small = np.where((mask_small == 2) | (mask_small == 0), 0, 1).astype('uint8')
    # 缩放到原始图像尺寸（最近邻插值保持二值性）
    mask2_original = cv2.resize(mask2_small, (w, h), interpolation=cv2.INTER_NEAREST)

    # 调用缺陷检测
    detect_brown_defects_single_box(img, mask2_original, min_area=20)
    # ===========================================================

    # 将原始图像的BGR通道与alpha通道（掩膜）合并，创建透明背景的PNG图像。
    b, g, r = cv2.split(img)
    alpha = mask2_original * 255
    img_rgba = cv2.merge((b, g, r, alpha))

    return img_rgba


if __name__ == '__main__':
    input_dir = 'imgs'
    output_dir = 'output2'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_list = [f for f in os.listdir(input_dir)]

    print(f"找到 {len(file_list)} 张图片，开始处理...")
    start_time = time.time()

    for i, img_file in enumerate(file_list):
        img_path = os.path.join(input_dir, img_file)
        print(f"[{i + 1}/{len(file_list)}] 正在处理: {img_file}...")

        # scale_factor缩放因子以保持较好的边缘和检测效果
        processed_img = remove_background_grabcut_fast(img_path, scale_factor=0.06, iter_count=2)

        if processed_img is not None:
            filename_base, _ = os.path.splitext(img_file)
            output_filename = filename_base + ".png"
            output_path = os.path.join(output_dir, output_filename)
            cv2.imwrite(output_path, processed_img)
        else:
            print(f"处理失败: {img_file}")

    end_time = time.time()
    print(f"\n全部完成！耗时: {end_time - start_time:.2f} 秒。结果保存在 {output_dir}")
