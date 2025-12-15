import cv2
import numpy as np
import os
import time
import matplotlib.pyplot as plt


# --- 保持原有的去背函数不变 ---
def remove_background_grabcut_fast(image_path, scale_factor=0.2, iter_count=2):
    img = cv2.imread(image_path)
    if img is None: return None
    h, w = img.shape[:2]

    # 缩放处理
    small_w = int(w * scale_factor)
    small_h = int(h * scale_factor)
    if small_w < 10 or small_h < 10: small_w, small_h = w, h
    small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_AREA)

    # 矩形初始化
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


# --- 核心修改：替换为液面凹陷检测逻辑 ---
def detect_single_best_defect(img_rgba):
    img_result = img_rgba.copy()

    # 转换颜色空间：从 BGRA 转为 BGR 以便进行 HSV 处理
    img_bgr = cv2.cvtColor(img_result, cv2.COLOR_BGRA2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # 1. 图像分割 (提取蓝色)
    mask = cv2.inRange(hsv, np.array([40, 170, 40]), np.array([130, 255, 255]))

    # 结合 Alpha 通道：如果背景已经被 GrabCut 移除（Alpha=0），则强制 Mask 为 0
    alpha = img_result[:, :, 3]
    mask = cv2.bitwise_and(mask, mask, mask=alpha)

    # 形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # plt.imshow(mask)
    # plt.show()

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # 未找到目标，直接返回原图（不做标注）
        return img_result, False

    # 找到最大轮廓
    max_cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_cnt)
    # print("Found contour:", x, y, w, h)

    # 宽度过滤
    if w < 450:
        return img_result, False

    pts = max_cnt.reshape(-1, 2)

    # 2. 寻找左右基准点 (几何极值法)
    # 仅在 Top 20% 区域内寻找角点
    y_cutoff_corner = y + h * 0.2
    corner_candidates = pts[pts[:, 1] < y_cutoff_corner]
    if len(corner_candidates) == 0: corner_candidates = pts

    # 左基点: x+y 最小; 右基点: y+(-x) 最小
    p_left = corner_candidates[np.argmin(corner_candidates.sum(axis=1))]
    p_right = corner_candidates[np.argmin(corner_candidates[:, 1] - corner_candidates[:, 0])]

    p_left = tuple(p_left)
    p_right = tuple(p_right)
    x1, y1 = p_left
    x2, y2 = p_right

    # 3. 计算凹陷逻辑
    # 定义 ROI 阈值线 (Top 5%)
    y_roi_limit = y + h * 0.05

    # 筛选 ROI 内的点
    valid_mask = (pts[:, 0] > x1) & (pts[:, 0] < x2) & (pts[:, 1] < y_roi_limit)

    roi_pts = pts[valid_mask]

    # 计算基准线斜率和理论 Y
    slope = (y2 - y1) / (x2 - x1)
    expected_y = y1 + slope * (roi_pts[:, 0] - x1)

    # 比较：实际 Y > 理论 Y 代表在下方 (凹陷)
    defects_mask = roi_pts[:, 1] > expected_y

    # 计算凹陷比例
    is_defect = False
    ratio = np.mean(defects_mask)
    if ratio > 0.5:
        is_defect = True

        # 【可视化】有凹陷 -> 画红框
        defect_pts = roi_pts[defects_mask]
        if len(defect_pts) > 0:
            dx, dy, dw, dh = cv2.boundingRect(defect_pts.astype(np.int32))
            # 外扩一点便于观察
            cv2.rectangle(img_result, (dx - 5, dy - 5), (dx + dw + 5, dy + dh + 5), (0, 0, 255, 255), 2)
            # 【可视化】始终绘制基准点(红色),基准线(蓝色),轮廓(绿色),限制线 (黄色)
            cv2.circle(img_result, p_left, 8, (0, 0, 255, 255), -1)
            cv2.circle(img_result, p_right, 8, (0, 0, 255, 255), -1)
            cv2.line(img_result, p_left, p_right, (0, 0, 0, 255), 2)
            cv2.drawContours(img_result, [max_cnt], -1, (0, 255, 0), 2)
            cv2.line(img_result, (x, int(y_roi_limit)), (x + w, int(y_roi_limit)), (0, 255, 255, 255), 1)
        # 标注文字
        cv2.putText(img_result, f"DEFECT (R:{ratio:.2f})", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255, 255), 2)

    return img_result, is_defect


if __name__ == '__main__':
    input_dir = 'imgs'
    output_dir = 'output4'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_list = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.png', '.bmp'))]
    print(f"找到 {len(file_list)} 张图片...")

    for img_file in file_list:
        img_path = os.path.join(input_dir, img_file)

        # 1. 去背 (Scale 设为 0.3 兼顾速度与效果)
        processed_img_rgba = remove_background_grabcut_fast(img_path, scale_factor=0.06, iter_count=2)

        if processed_img_rgba is not None:
            # 2. 液面凹陷检测 (无论结果如何都返回处理后的图)
            result_img, has_defect = detect_single_best_defect(processed_img_rgba)

            # 3. 保存
            status = "_FOUND" if has_defect else "_CLEAN"
            save_name = f"{os.path.splitext(img_file)[0]}{status}.png"
            cv2.imwrite(os.path.join(output_dir, save_name), result_img)

            print(f"处理: {img_file} -> {status}")
