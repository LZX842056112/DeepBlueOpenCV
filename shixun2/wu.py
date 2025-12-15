import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


# ==========================================
# 1. 去背函数 (保持原样，未修改)
# ==========================================
def remove_background_grabcut_fast(image_path, scale_factor=0.06, iter_count=2):
    img = cv2.imread(image_path)
    if img is None: return None
    h, w = img.shape[:2]

    # 为了速度，在小图上计算mask
    small_w = int(w * scale_factor)
    small_h = int(h * scale_factor)
    if small_w < 10 or small_h < 10: small_w, small_h = w, h

    small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_AREA)

    rect_small = (int(small_w * 0.2), int(small_h * 0.05), int(small_w * 0.6), int(small_h * 0.9))
    mask_small = np.zeros(small_img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(small_img, mask_small, rect_small, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)
    except:
        return None

    mask2_small = np.where((mask_small == 2) | (mask_small == 0), 0, 1).astype('uint8')
    mask2_original = cv2.resize(mask2_small, (w, h), interpolation=cv2.INTER_NEAREST)

    b, g, r = cv2.split(img)
    alpha = mask2_original * 255
    img_rgba = cv2.merge((b, g, r, alpha))

    return img_rgba


# ==========================================
# 2. 核心检测逻辑 (重构：极简版)
# ==========================================
def detect_defects(img_rgba):
    """
    利用形态学操作代替几何计算，实现ROI提取和污渍合并。
    """
    bgr = img_rgba[:, :, :3]
    alpha = img_rgba[:, :, 3]
    h, w = alpha.shape[:2]
    result_img = img_rgba.copy()

    # --- A. ROI 生成 (利用腐蚀代替 minAreaRect) ---
    # 逻辑：试管边缘通常有反光，直接将 Alpha 通道向内腐蚀约 15-20% 的宽度，
    # 剩下的就是安全的中心区域，无论试管是斜的还是直的。
    erode_size = int(min(w, h) * 0.04)  # 动态计算腐蚀力度
    kernel_roi = cv2.getStructuringElement(cv2.MORPH_RECT, (erode_size,erode_size))
    roi_mask = cv2.erode(alpha, kernel_roi)

    # --- B. 颜色检测 (保持原逻辑) ---
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)


    # 保持你设定的阈值 (注: Value 120-150 是非常窄的特定灰度范围)
    color_mask = cv2.inRange(hsv, np.array([0, 0, 120]), np.array([180, 255, 150]))

    # --- C. 综合掩膜 ---
    # 只有在 ROI 区域内 且 符合颜色阈值 的才算
    valid_mask = cv2.bitwise_and(color_mask, color_mask, mask=roi_mask)


    # --- D. 物理合并 (利用膨胀代替 merge_boxes) ---
    # 逻辑：如果两个点离得近，把它们都"变胖"直到粘在一起，算作一个物体。
    # 40px 是你原代码的合并阈值，这里用 20px 的核膨胀 (两边各扩20约等于距离40)
    merge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    merged_mask = cv2.dilate(valid_mask, merge_kernel, iterations=3)

    # --- E. 轮廓提取与筛选 ---
    contours, _ = cv2.findContours(merged_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    final_boxes = []

    for c in contours:
        area = cv2.contourArea(c)
        # 因为膨胀过，面积阈值需要适当放宽，或者计算原始 mask 的面积(更精准)
        # 这里为了简单，直接复用边界框去原始 mask 统计像素点
        x, y, bw, bh = cv2.boundingRect(c)

        # 裁剪出该区域的原始 mask (未膨胀的) 来判断真实面积
        roi_raw = valid_mask[y:y + bh, x:x + bw]
        true_area = cv2.countNonZero(roi_raw)

        # 原逻辑：20 < area < 400，长宽比 0.5 - 2.0
        if 20 < true_area < 400:
            ratio = float(bw) / bh
            if 0.5 < ratio < 2.0:
                final_boxes.append((x, y, bw, bh))
                # 绘制 (红色框)
                cv2.rectangle(result_img, (x, y), (x + bw, y + bh), (0, 0, 255, 255), 2)

    return result_img, len(final_boxes)


# ==========================================
# 3. 主入口
# ==========================================
def main():
    input_folder = 'imgs'
    output_folder = 'output_final'
    os.makedirs(output_folder, exist_ok=True)  # 一行代码创建目录

    valid_exts = {'.jpg', '.jpeg', '.png', '.bmp'}

    # 列表推导式获取文件
    files = [f for f in os.listdir(input_folder) if os.path.splitext(f)[1].lower() in valid_exts]
    print(f"开始处理 {len(files)} 张图片...")

    for filename in files:
        file_path = os.path.join(input_folder, filename)

        # 1. 去背
        img_rgba = remove_background_grabcut_fast(file_path)

        if img_rgba is not None:
            # 2. 检测
            final_img, defect_count = detect_defects(img_rgba)

            # 3. 保存
            tag = "FOUND" if defect_count > 0 else "CLEAN"
            save_name = f"{os.path.splitext(filename)[0]}_{tag}.png"
            cv2.imwrite(os.path.join(output_folder, save_name), final_img)

            print(f"[{'发现' if defect_count else '干净'}] {filename}: {defect_count} 处")
        else:
            print(f"[错误] {filename}")


if __name__ == '__main__':
    main()