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


# --- 核心修改：只找一个最精准的缺陷 ---
# --- 修改后的 detect_single_best_defect 函数 ---
def detect_single_best_defect(img_rgba):
    """
    只检测最明显的一个缺陷，并过滤掉蓝线、噪点以及过大的可能是试管本身的区域
    """
    img_result = img_rgba.copy()
    h, w = img_result.shape[:2]

    # 图像预处理
    gray = cv2.cvtColor(img_result, cv2.COLOR_BGRA2GRAY)
    # 提取alpha通道（透明度掩膜）
    alpha_mask = img_result[:, :, 3]

    # Canny边缘检测，低阈值30，高阈值100
    edges = cv2.Canny(gray, 30, 100)
    # 只在前景区域（alpha通道非零）检测边缘
    edges = cv2.bitwise_and(edges, edges, mask=alpha_mask)

    # 屏蔽干扰区域
    # 屏蔽左侧盖子 (加大比例确保盖子完全不被检测)
    cap_region = int(w * 0.28)
    # 将该区域边缘置零
    edges[:, :cap_region] = 0

    # (B) 屏蔽上下边缘 (防止管壁反光)
    margin = 8
    edges[:margin, :] = 0
    edges[h - margin:, :] = 0

    # 4. 形态学处理
    # 使用较小的核进行膨胀，保证框更贴合（精准），不要扩得太大
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # 膨胀2次，连接断开的边缘，使缺陷区域更连贯
    dilated = cv2.dilate(edges, kernel, iterations=2)
    # 闭运算填充内部孔洞
    dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)


    # 5. 查找轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []

    for cnt in contours:
        # 获取边界矩形
        x, y, rect_w, rect_h = cv2.boundingRect(cnt)
        # 计算轮廓面积
        area = cv2.contourArea(cnt)

        # --- 精细过滤条件 ---

        # 1. 面积阈值：太小的白点忽略
        if area < 80: continue

        # 2. 形状过滤（核心）：排除蓝线
        # 缺陷通常是块状的，蓝线是长条状的
        # 计算宽高比
        aspect_ratio = rect_w / float(rect_h)

        # 如果宽度超过图片的一半，肯定是那条线 -> 排除
        if rect_w > w * 0.4: continue

        # 如果宽高比特别大（例如宽是高的5倍），说明是扁长的线 -> 排除
        if aspect_ratio > 5.0: continue

        # 如果高度特别大且宽度很窄（竖线干扰）-> 排除
        if rect_h > h * 0.5 and rect_w < 20: continue

        # 将符合条件的轮廓加入候选列表
        candidates.append(cnt)

    # 标记是否找到缺陷
    found_defect = False

    # 6. 决策：只取一个最匹配的
    if len(candidates) > 0:
        # 按面积排序，取最大的一个（通常最大的异常块就是碎片）
        best_cnt = max(candidates, key=cv2.contourArea)

        # 获取边界框
        x, y, rect_w, rect_h = cv2.boundingRect(best_cnt)

        MAX_RATIO = 0.6
        if rect_w > w * MAX_RATIO or rect_h > h * MAX_RATIO:
            # 如果框太大，则认为不是缺陷，跳过标记
            pass
        else:
            # 否则正常绘制缺陷框和标注
            cv2.rectangle(img_result, (x, y), (x + rect_w, y + rect_h), (0, 0, 255, 255), 2)
            cv2.putText(img_result, f"Defect", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255, 255), 1)
            found_defect = True

    return img_result, found_defect


if __name__ == '__main__':
    input_dir = 'imgs'
    output_dir = 'output3'  # 新的输出文件夹

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_list = [f for f in os.listdir(input_dir)]
    print(f"找到 {len(file_list)} 张图片...")

    for img_file in file_list:
        img_path = os.path.join(input_dir, img_file)

        # 1. 去背 (保持精度，Scale设为0.3)
        processed_img_rgba = remove_background_grabcut_fast(img_path, scale_factor=0.06, iter_count=2)

        if processed_img_rgba is not None:
            # 2. 精准检测
            result_img, has_defect = detect_single_best_defect(processed_img_rgba)

            # 3. 保存
            status = "_FOUND" if has_defect else "_CLEAN"
            cv2.imwrite(os.path.join(output_dir, f"{os.path.splitext(img_file)[0]}{status}.png"), result_img)
            print(f"处理: {img_file} -> {status}")