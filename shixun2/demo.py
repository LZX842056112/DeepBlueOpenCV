import cv2
import numpy as np
import os
import time
import matplotlib.pyplot as plt


# 使用GrabCut算法获取前景掩码（前景分割）
def get_foreground_mask(img, scale_factor=0.06, iter_count=2):
    # 获取原始图像尺寸
    h, w = img.shape[:2]

    # 计算缩小后的尺寸（加速GrabCut处理）
    small_w = int(w * scale_factor)
    small_h = int(h * scale_factor)

    # 缩小图像
    small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_AREA)

    # 定义前景矩形区域（GrabCut初始框，覆盖图像中央大部分区域）
    # 假设物体位于图像中心，排除边缘区域（左边20%，上边5%，保留中间60%宽和90%高）
    rect_small = (int(small_w * 0.2), int(small_h * 0.05), int(small_w * 0.6), int(small_h * 0.9))

    # 创建与缩小图像同尺寸的掩码，初始化为全0（背景）
    mask_small = np.zeros(small_img.shape[:2], np.uint8)

    # 创建GrabCut算法需要的临时数组（65个混合高斯分量）
    bgdModel = np.zeros((1, 65), np.float64)  # 背景模型
    fgdModel = np.zeros((1, 65), np.float64)  # 前景模型

    try:
        # 执行GrabCut算法进行前景分割
        # 参数说明：
        # - small_img: 输入图像
        # - mask_small: 初始/输出掩码
        # - rect_small: 包含前景的矩形区域
        # - bgdModel, fgdModel: 背景/前景模型
        # - iter_count: 迭代次数
        # - cv2.GC_INIT_WITH_RECT: 使用矩形初始化
        cv2.grabCut(small_img, mask_small, rect_small, bgdModel, fgdModel, iter_count, cv2.GC_INIT_WITH_RECT)
    except:
        # 如果GrabCut失败，返回None和False
        return None, False

    # 处理GrabCut输出的掩码：
    # GrabCut掩码值说明：
    # 0 - 确定背景，1 - 确定前景，2 - 可能背景，3 - 可能前景
    # 将确定前景(1)和可能前景(3)设为1，其他设为0
    mask2_small = np.where((mask_small == 2) | (mask_small == 0), 0, 1).astype('uint8')

    # 将缩小后的掩码恢复到原始尺寸（使用最近邻插值保持二值性）
    mask2_original = cv2.resize(mask2_small, (w, h), interpolation=cv2.INTER_NEAREST)

    return mask2_original, True


# 检测凹痕
def find_indentation_defect(original_img, mask):
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)
    # 定义蓝色的HSV范围（用于检测蓝色区域）
    blue_mask = cv2.inRange(hsv, np.array([40, 170, 40]), np.array([130, 255, 255]))
    # 只在前景区域内检测蓝色
    blue_mask = cv2.bitwise_and(blue_mask, blue_mask, mask=mask)
    # 创建7x7矩形结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # 闭运算：填充蓝色区域内部的小孔洞
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
    # 开运算：去除小的蓝色噪点
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    # 寻找蓝色区域的轮廓
    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    # 找到最大的蓝色区域
    max_cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_cnt)
    # 宽度过滤：宽度小于450像素的忽略
    if w < 450:
        return None
    # 将轮廓点转换为二维数组
    pts = max_cnt.reshape(-1, 2)
    # 定义感兴趣区域的上限（顶部5%区域）
    y_roi_limit = y + h * 0.05
    # 筛选出位于顶部的点（上5%区域），用于寻找左右顶点
    corner_candidates = pts[pts[:, 1] < y_roi_limit]
    if len(corner_candidates) > 0:
        # 左角点：x+y最小的点（最左上的点）
        p_left = corner_candidates[np.argmin(corner_candidates.sum(axis=1))]
        # 右角点：y-x最小的点（即 y 较小且 x 较大的点，右上角方向）
        p_right = corner_candidates[np.argmin(corner_candidates[:, 1] - corner_candidates[:, 0])]
    else:
        return None

    x1, y1 = p_left
    x2, y2 = p_right
    # 选取位于左右角点之间，且在特定高度范围内的点
    valid_mask_idx = (pts[:, 0] > x1) & (pts[:, 0] < x2) & (pts[:, 1] < y_roi_limit)
    roi_pts = pts[valid_mask_idx]
    if len(roi_pts) == 0:
        return None
    # 计算左右角点连线的斜率
    slope = (y2 - y1) / (x2 - x1)
    # 根据直线方程计算每个x坐标对应的预期y值
    expected_y = y1 + slope * (roi_pts[:, 0] - x1)
    # 检测凹痕：实际y值大于预期y值的点（即向下凹陷的点）
    defects_mask = roi_pts[:, 1] > expected_y
    # 计算缺陷点占ROI总点数的比例
    ratio = np.mean(defects_mask)
    # 如果凹痕点比例超过50%，则认为存在凹痕缺陷
    if ratio > 0.5:
        # 获取凹痕区域的外接矩形
        defect_pts = roi_pts[defects_mask]
        dx, dy, dw, dh = cv2.boundingRect(defect_pts.astype(np.int32))

        return {
            'type': 'INDENTATION',  # 缺陷类型：凹痕
            'rect': (x, y, w, h),  # 蓝色区域的外接矩形
            'defect_rect': (dx, dy, dw, dh),  # 凹痕区域的外接矩形
            'color': (0, 0, 255),  # 红色
            'ratio': ratio,  # 凹痕点比例
            'p_left': tuple(p_left),  # 左角点坐标
            'p_right': tuple(p_right),  # 右角点坐标
            'roi_y_limit': int(y_roi_limit),  # ROI上限
            'contour': max_cnt  # 蓝色区域轮廓
        }

    return None


# 检测褐色斑点缺陷
def find_brown_candidate(original_img, mask, min_area=20):
    # 将图像从 BGR 转为 HSV 颜色空间，利于颜色分割
    hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)
    # 定义褐色的HSV范围
    lower_brown = np.array([10, 80, 0])
    upper_brown = np.array([30, 255, 200])
    # 生成掩膜
    color_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    # 只在前景区域内检测褐色
    final_mask = cv2.bitwise_and(color_mask, color_mask, mask=mask)
    # 形态学开操作（先腐蚀后膨胀），去除小噪声点
    kernel = np.ones((3, 3), np.uint8)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)

    # 寻找轮廓
    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    best_rect = None

    # 遍历所有轮廓，寻找面积最大的
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            if area > max_area:
                max_area = area
                best_rect = cv2.boundingRect(cnt)

    if best_rect:
        return {
            'type': 'SPOT',  # 缺陷类型：斑点
            'rect': best_rect,  # 外接矩形
            'color': (0, 165, 255)  # 橙色
        }

    return None


# 检测碎片缺陷
def find_debris_candidate(original_img, mask):
    # 获取图像尺寸
    h, w = original_img.shape[:2]
    # 转为灰度图
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    # 创建亮度掩码，排除过亮区域
    _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    # 结合前景掩码和亮度掩码，排除高光区域
    processed_mask = cv2.bitwise_and(mask, bright_mask)
    # 使用Canny边缘检测（低阈值30，高阈值100）
    edges = cv2.Canny(gray, 30, 100)
    # 只在处理后的前景区域内检测边缘
    edges = cv2.bitwise_and(edges, edges, mask=processed_mask)

    # 创建3x3矩形结构元素用于形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # 对边缘图像进行膨胀操作，连接断开的边缘
    dilated = cv2.dilate(edges, kernel, iterations=2)
    # 进行闭运算，填充小孔洞
    dilated = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    # 寻找轮廓（只检测外部轮廓，使用简单近似）
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []  # 候选轮廓列表
    for cnt in contours:
        # 获取轮廓的外接矩形
        x, y, rect_w, rect_h = cv2.boundingRect(cnt)
        # 宽高比过滤：排除细长条状物体
        aspect_ratio = rect_w / float(rect_h)
        if aspect_ratio > 5.0:
            continue
        # 通过所有过滤的轮廓加入候选列表
        candidates.append(cnt)

    # 如果有候选轮廓
    if candidates:
        # 选择面积最大的候选轮廓
        best_cnt = max(candidates, key=cv2.contourArea)
        x, y, rect_w, rect_h = cv2.boundingRect(best_cnt)
        # 最终尺寸检查：不能超过图像的50%
        MAX_RATIO = 0.5
        if rect_w > w * MAX_RATIO or rect_h > h * MAX_RATIO:
            return None
        # 返回碎片信息字典
        return {
            'type': 'DEBRIS',  # 缺陷类型：碎片
            'rect': (x, y, rect_w, rect_h),  # 外接矩形
            'color': (0, 0, 255)  # 红色(BGR格式)
        }
    return None

# 检测暗斑缺陷
def find_dark_spot_morph(original_img, mask):
    # 获取掩码尺寸
    h, w = mask.shape[:2]
    # 计算腐蚀核大小（图像尺寸的4%）
    erode_size = int(min(w, h) * 0.04)
    # 确保核大小为奇数
    if erode_size % 2 == 0:
        erode_size += 1
    # 创建矩形结构元素用于腐蚀操作
    kernel_roi = cv2.getStructuringElement(cv2.MORPH_RECT, (erode_size, erode_size))
    # 腐蚀掩码，缩小前景区域（去除边缘区域）
    roi_mask = cv2.erode(mask, kernel_roi)
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)
    # 定义暗色区域的HSV范围（低亮度范围）
    color_mask = cv2.inRange(hsv, np.array([0, 0, 120]), np.array([180, 255, 150]))
    # 在腐蚀后的前景区域内检测暗色
    valid_mask = cv2.bitwise_and(color_mask, color_mask, mask=roi_mask)
    # 使用椭圆核进行膨胀，合并相邻的细碎暗点
    merge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    merged_mask = cv2.dilate(valid_mask, merge_kernel, iterations=3)
    # 寻找轮廓
    contours, _ = cv2.findContours(merged_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    found_candidates = []  # 候选暗斑列表
    for c in contours:
        # 获取轮廓的外接矩形
        x, y, bw, bh = cv2.boundingRect(c)
        # 在原掩码中提取对应区域
        roi_raw = valid_mask[y:y + bh, x:x + bw]
        # 计算实际暗斑像素数量
        true_area = cv2.countNonZero(roi_raw)
        # 面积过滤：20-200像素之间
        if 20 < true_area < 400:
            # 宽高比在 0.5 到 2.0 之间（接近圆形或方形，不是细长条）
            ratio = float(bw) / bh
            if 0.5 < ratio < 2.0:
                found_candidates.append({
                    'type': 'DARK',  # 缺陷类型：暗斑
                    'rect': (x, y, bw, bh),  # 外接矩形
                    'area': true_area,  # 实际面积
                    'color': (128, 0, 128)  # 紫色
                })

    # 如果有候选暗斑，返回面积最大的一个
    if found_candidates:
        return max(found_candidates, key=lambda x: x['area'])

    return None


if __name__ == '__main__':
    # 输入输出目录设置
    input_dir = 'imgs'
    output_dir = 'output'

    # 如果输出目录不存在，则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取输入目录中所有文件的列表
    file_list = [f for f in os.listdir(input_dir)]
    print(f"找到 {len(file_list)} 张图片，开始处理...")

    # 记录开始时间
    start_time = time.time()

    for img_file in file_list:
        img_path = os.path.join(input_dir, img_file)
        original_img = cv2.imread(img_path)

        # 获取前景掩码
        mask, success = get_foreground_mask(original_img, scale_factor=0.06, iter_count=2)

        if success:
            detected_defects = []  # 检测到的缺陷列表

            # 依次调用四个缺陷检测函数
            res_indentation = find_indentation_defect(original_img, mask)
            res_brown = find_brown_candidate(original_img, mask, min_area=20)
            res_debris = find_debris_candidate(original_img, mask)
            res_dark = find_dark_spot_morph(original_img, mask)

            # 将检测到的缺陷添加到列表中
            if res_indentation:
                detected_defects.append(res_indentation)
            if res_debris:
                detected_defects.append(res_debris)
            if res_brown:
                detected_defects.append(res_brown)
            if res_dark:
                detected_defects.append(res_dark)

            # 复制原图用于画图
            final_draw_img = original_img.copy()

            # 用于构建文件名的标签列表
            filename_tags = []

            # 如果没有检测到任何缺陷
            if not detected_defects:
                # 如果没检测到任何缺陷，标记为 CLEAN
                filename_tags.append("CLEAN")
            else:
                # 遍历所有检测到的缺陷
                for defect in detected_defects:
                    d_type = defect['type']
                    rect = defect['rect']
                    color = defect['color']
                    x, y, w, h = rect

                    if d_type not in filename_tags:
                        filename_tags.append(d_type)

                    # 特殊处理凹痕缺陷
                    if d_type == 'INDENTATION':
                        ratio = defect['ratio']  # 凹痕比例
                        p_left = defect['p_left']
                        p_right = defect['p_right']
                        y_limit = defect['roi_y_limit']  # ROI上限
                        cnt = defect['contour']  # 蓝色区域轮廓
                        dx, dy, dw, dh = defect['defect_rect']  # 凹痕矩形
                        # 绘制蓝色区域轮廓（绿色）
                        cv2.drawContours(final_draw_img, [cnt], -1, (0, 255, 0), 2)
                        # 绘制左右角点（红色圆点）
                        cv2.circle(final_draw_img, p_left, 8, (0, 0, 255), -1)
                        cv2.circle(final_draw_img, p_right, 8, (0, 0, 255), -1)
                        # 绘制左右角点连线（黑色）
                        cv2.line(final_draw_img, p_left, p_right, (0, 0, 0), 2)
                        # 绘制ROI上限线（黄色）
                        cv2.line(final_draw_img, (x, y_limit), (x + w, y_limit), (0, 255, 255), 1)
                        # 凹痕标签文本
                        label_text = f"INDENTATION-DEFECT (R:{ratio:.2f})"
                        cv2.putText(final_draw_img, label_text, (x, y - 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        # 标记凹痕区域（红色）
                        cv2.rectangle(final_draw_img, (dx - 5, dy - 5),
                                      (dx + dw + 5, dy + dh + 5), (0, 0, 255, 255), 2)
                    else:
                        pad = 2
                        cv2.rectangle(final_draw_img, (max(0, x - pad), max(0, y - pad)),
                                      (x + w + pad, y + h + pad), color, 3)

                        # 添加缺陷类型标签
                        cv2.putText(final_draw_img, d_type, (x, y - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # 构建输出文件名：原文件名_缺陷标签.jpg
            status_str = "_" + "_".join(filename_tags)
            output_filename = f"{os.path.splitext(img_file)[0]}{status_str}.jpg"
            save_path = os.path.join(output_dir, output_filename)
            cv2.imwrite(save_path, final_draw_img)
            print(f"处理: {img_file} -> {status_str}")
        else:
            print(f"GrabCut 失败: {img_file}")

    end_time = time.time()
    print(f"\n全部完成！耗时: {end_time - start_time:.2f} 秒。结果保存在 {output_dir}")
