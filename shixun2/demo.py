import random
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import time

# 预创建常用结构元素（避免反复创建）
KERNEL_7 = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
KERNEL_3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))


# 使用GrabCut算法获取前景掩码（前景分割）
def get_foreground_mask(img, scale_factor=0.06, iter_count=2):
    if img is None:
        return None, False

    h, w = img.shape[:2]
    # 计算缩小后的尺寸
    sw = int(w * scale_factor)
    sh = int(h * scale_factor)
    # 缩小图像
    small_img = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
    # 定义前景矩形区域（GrabCut初始框，覆盖图像中央大部分区域）
    # 假设物体位于图像中心，排除边缘区域（左边20%，上边5%，保留中间60%宽和90%高）
    rect = (int(sw * 0.2), int(sh * 0.05), int(sw * 0.6), int(sh * 0.9))
    # 创建与缩小图像同尺寸的掩码，初始化为全0（背景）
    mask = np.zeros((sh, sw), np.uint8)
    # 创建GrabCut算法需要的临时数组（65个混合高斯分量）
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(small_img, mask, rect, bgd, fgd, iter_count, cv2.GC_INIT_WITH_RECT)
    except Exception:
        return None, False
    # 处理GrabCut输出的掩码：
    # GrabCut掩码值说明：
    # 0 - 确定背景，1 - 确定前景，2 - 可能背景，3 - 可能前景
    # 将确定前景(1)和可能前景(3)设为1，其他设为0
    mask = np.where((mask == 0) | (mask == 2), 0, 1).astype(np.uint8)
    # 将缩小后的掩码恢复到原始尺寸（使用最近邻插值保持二值性）
    mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    return mask, True


# 检测凹痕
def find_indentation_defect(img, hsv, mask):
    # 定义蓝色的HSV范围（用于检测蓝色区域）
    blue = cv2.inRange(hsv, np.array([40, 170, 40]), np.array([130, 255, 255]))
    # 只在前景区域内检测蓝色
    blue = cv2.bitwise_and(blue, blue, mask=mask)
    # 闭运算：填充蓝色区域内部的小孔洞
    blue = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, KERNEL_7)
    # 开运算：去除小的蓝色噪点
    blue = cv2.morphologyEx(blue, cv2.MORPH_OPEN, KERNEL_7)
    # 寻找蓝色区域的轮廓
    contours, _ = cv2.findContours(blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    # 找到最大的蓝色区域
    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    # 宽度过滤：宽度小于450像素的忽略
    if w < 450:
        return None
    # 将轮廓点转换为二维数组
    pts = cnt.reshape(-1, 2)
    # 定义感兴趣区域的上限（顶部5%区域）
    y_limit = y + h * 0.05
    # 筛选出位于顶部的点（顶部5%区域），用于寻找左右顶点
    top_pts = pts[pts[:, 1] < y_limit]
    if len(top_pts) == 0:
        return None
    # 左角点：x+y最小的点（最左上的点）
    p_left = top_pts[np.argmin(top_pts.sum(axis=1))]
    # 右角点：y+(-x)最小的点（即 y 较小且 x 较大的点，右上角方向）
    p_right = top_pts[np.argmin(top_pts[:, 1] - top_pts[:, 0])]

    x1, y1 = p_left
    x2, y2 = p_right
    if x2 == x1:
        return None
    # 选取位于左右角点之间，且在特定高度范围内的点
    roi_pts = pts[(pts[:, 0] > x1) & (pts[:, 0] < x2) & (pts[:, 1] < y_limit)]
    if len(roi_pts) == 0:
        return None
    # 计算左右角点连线的斜率
    slope = (y2 - y1) / (x2 - x1)
    # 根据直线方程计算每个x坐标对应的预期y值
    y_expected = y1 + slope * (roi_pts[:, 0] - x1)
    # 检测凹痕：实际y值大于预期y值的点（即向下凹陷的点）
    defect_mask = roi_pts[:, 1] > y_expected
    # 计算缺陷点占ROI总点数的比例
    ratio = np.mean(defect_mask)
    # 如果凹痕点比例超过50%，则认为存在凹痕缺陷
    if ratio <= 0.5:
        return None
    # 获取凹痕区域的外接矩形
    defect_pts = roi_pts[defect_mask]
    dx, dy, dw, dh = cv2.boundingRect(defect_pts.astype(np.int32))

    return {
        'type': 'INDENTATION',
        'rect': (x, y, w, h),  # 蓝色区域的外接矩形
        'defect_rect': (dx, dy, dw, dh),  # 凹痕区域的外接矩形
        'p_left': tuple(p_left),
        'p_right': tuple(p_right),
        'contour': cnt,  # 蓝色区域轮廓
        'color': (0, 0, 255)  # 红色
    }


# 褐色斑点检测
def find_brown_candidate(hsv, mask):
    # 定义褐色的HSV范围
    lower = np.array([10, 80, 0])
    upper = np.array([30, 255, 200])
    # 生成掩膜
    brown = cv2.inRange(hsv, lower, upper)
    # 只在前景区域内检测褐色
    brown = cv2.bitwise_and(brown, brown, mask=mask)
    # 形态学开操作（先腐蚀后膨胀），去除小噪声点
    brown = cv2.morphologyEx(brown, cv2.MORPH_OPEN, KERNEL_3)

    contours, _ = cv2.findContours(brown, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best = None
    best_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > best_area:
            best = cv2.boundingRect(c)
            best_area = area

    if best:
        return {'type': 'SPOT',
                'rect': best,  # 外接矩形
                'color': (0, 165, 255)  # 橙色
                }
    return None


# 检测碎片缺陷
def find_debris_candidate(gray, mask, img_shape):
    h, w = img_shape[:2]
    # 创建亮度掩码，排除过亮区域
    _, bright = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    # 结合前景掩码和亮度掩码，排除高光区域
    valid = cv2.bitwise_and(mask, bright)

    # 使用Canny边缘检测（低阈值30，高阈值100）
    edges = cv2.Canny(gray, 30, 100)
    # 只在处理后的前景区域内检测边缘
    edges = cv2.bitwise_and(edges, edges, mask=valid)

    # 对边缘图像进行膨胀操作，连接断开的边缘
    edges = cv2.dilate(edges, KERNEL_3, iterations=2)
    # 进行闭运算，填充小孔洞
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, KERNEL_3)

    # 寻找轮廓（只检测外部轮廓，使用简单近似）
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 候选轮廓列表
    candidates = []

    for c in contours:
        x, y, rw, rh = cv2.boundingRect(c)
        # 宽高比过滤：排除细长条状物体
        if rh == 0 or rw / rh > 5:
            continue
        candidates.append(c)

    if not candidates:
        return None

    # 选择面积最大的候选轮廓
    best = max(candidates, key=cv2.contourArea)
    x, y, rw, rh = cv2.boundingRect(best)
    # 最终尺寸检查：不能超过图像的50%
    if rw > w * 0.5 or rh > h * 0.5:
        return None

    return {'type': 'DEBRIS',
            'rect': (x, y, rw, rh),
            'color': (0, 0, 255)  # 红色
            }


# 暗斑检测
def find_dark_spot(hsv, mask):
    h, w = mask.shape
    # 计算腐蚀核大小（图像尺寸的4%）
    k = int(min(w, h) * 0.04)
    # 确保核大小为奇数
    if k % 2 == 0:
        k += 1
    # 创建矩形结构元素用于腐蚀操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    # 腐蚀掩码，缩小前景区域（去除边缘区域）
    roi_mask = cv2.erode(mask, kernel)
    # 定义暗色区域的HSV范围
    color_mask = cv2.inRange(hsv, np.array([0, 0, 120]), np.array([180, 255, 150]))
    # 在腐蚀后的前景区域内检测暗色
    valid_mask = cv2.bitwise_and(color_mask, color_mask, mask=roi_mask)
    # 使用椭圆核进行膨胀，合并相邻的细碎暗点
    merge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    merged_mask = cv2.dilate(valid_mask, merge_kernel, iterations=3)

    contours, _ = cv2.findContours(merged_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    best_area = 0
    for c in contours:
        # 获取轮廓的外接矩形
        x, y, bw, bh = cv2.boundingRect(c)
        # 在原掩码中提取对应区域
        roi = valid_mask[y:y + bh, x:x + bw]
        # 计算实际暗斑像素数量
        area = cv2.countNonZero(roi)
        # 面积过滤：20-400像素之间
        if 20 < area < 400:
            # 宽高比在 0.5 到 2.0 之间（接近圆形或方形，不是细长条）
            ratio = float(bw) / bh
            if 0.5 < ratio < 2.0:
                # 如果有候选暗斑，返回面积最大的一个
                if area > best_area:
                    best_area = area
                    best = (x, y, bw, bh)

    if best:
        return {'type': 'DARK', 'rect': best, 'color': (128, 0, 128)}
    return None


if __name__ == '__main__':
    input_dir = 'imgs'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    files = os.listdir(input_dir)
    print(f"找到 {len(files)} 张图片，开始处理...")
    start = time.time()

    for name in files:
        img = cv2.imread(os.path.join(input_dir, name))
        # 获取前景掩码
        mask, ok = get_foreground_mask(img)
        if not ok:
            print(f"GrabCut失败: {name}")
            continue

        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 转为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检测到的缺陷列表
        defects = []
        # 依次调用四个缺陷检测函数
        for res in (
                find_indentation_defect(img, hsv, mask),
                find_brown_candidate(hsv, mask),
                find_debris_candidate(gray, mask, img.shape),
                find_dark_spot(hsv, mask),
        ):
            # 将检测到的缺陷添加到列表中
            if res:
                defects.append(res)
        # 用于构建文件名的标签列表
        tags = []
        if not defects:
            tags.append("CLEAN")
        # 复制原图用于画图
        draw = img.copy()
        # 遍历所有检测到的缺陷
        for d in defects:
            x, y, w, h = d['rect']
            d_type = d['type']
            if d_type not in tags:
                tags.append(d_type)

            if d_type == 'INDENTATION':
                p_left = d['p_left']
                p_right = d['p_right']
                cnt = d['contour']  # 蓝色区域轮廓
                dx, dy, dw, dh = d['defect_rect']  # 凹痕矩形
                # 绘制蓝色区域轮廓（绿色）
                cv2.drawContours(draw, [cnt], -1, (0, 255, 0), 2)
                # 绘制左右角点（红色圆点）
                cv2.circle(draw, p_left, 6, (0, 0, 255), -1)
                cv2.circle(draw, p_right, 6, (0, 0, 255), -1)
                # 绘制左右角点连线（黑色）
                cv2.line(draw, p_left, p_right, (0, 0, 0), 2)
                # 标记凹痕区域（红色）
                cv2.rectangle(draw, (dx, dy), (dx + dw, dy + dh), (0, 0, 255), 2)
            else:
                cv2.rectangle(draw, (x, y), (x + w, y + h), d['color'], 2)

        out_name = f"{os.path.splitext(name)[0]}_{'_'.join(tags)}.bmp"
        cv2.imwrite(os.path.join(output_dir, out_name), draw)
        print(f"{name} -> {tags}")

    print(f"完成，耗时 {time.time() - start:.2f}s")
