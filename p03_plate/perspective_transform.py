"""
这是一个用于车牌透视变换的程序，主要功能是将倾斜拍摄的车牌图像校正为水平的长方形图像
"""
import cv2 as cv
import numpy as np
import os


def detect_blue_quadrilateral(image, debug=False):
    """
    蓝色四边形检测函数
    输入：原始 BGR 图像，调试标志
    输出：四边形的 4 个顶点坐标，或 None（未检测到）
    """
    # 转换到 HSV 颜色空间
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    
    # 尝试多个蓝色范围
    blue_ranges = [
        # 标准蓝色
        (np.array([100, 150, 50]), np.array([140, 255, 255])),
        # 更宽色调范围
        (np.array([90, 100, 50]), np.array([150, 255, 255])),
        # 更低饱和度
        (np.array([100, 50, 50]), np.array([140, 255, 255])),
    ]
    
    # 初始化轮廓和区域
    best_contour = None
    best_area = 0
    
    # 遍历多个蓝色范围
    for lower_blue, upper_blue in blue_ranges:
        # 创建蓝色掩码，蓝色区域为白色(255)，其他为黑色(0)
        blue_mask = cv.inRange(hsv, lower_blue, upper_blue)
        
        # 形态学操作，创建核
        kernel = np.ones((3, 3), np.uint8)
        # 闭合操作：填充空洞（白车牌上的黑点）
        blue_mask = cv.morphologyEx(blue_mask, cv.MORPH_CLOSE, kernel)
        # 开操作：去除噪声（黑背景上的白点）
        blue_mask = cv.morphologyEx(blue_mask, cv.MORPH_OPEN, kernel)
        
        # 查找所有外部轮廓
        # cv.RETR_EXTERNAL：只检测最外层轮廓
        # cv.CHAIN_APPROX_SIMPLE：轮廓近似方法，压缩水平、垂直和对角线段，只保留端点，减少轮廓点的数量，对于矩形等规则形状特别有效
        contours, _ = cv.findContours(blue_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大的轮廓
            # contours：列表，包含多个轮廓；每个轮廓：NumPy数组，形状为(n, 1, 2)，包含 n个点的坐标
            # max()：找出列表中的最大值，直接比较列表元素（但轮廓不能直接比较），使用 key 参数指定比较依据
            # key=cv.contourArea：计算轮廓的面积，按面积大小进行比较
            largest_contour = max(contours, key=cv.contourArea)
            # 计算最大轮廓的面积
            area = cv.contourArea(largest_contour)
            
            # 近似轮廓为多边形
            # 设置近似精度，为轮廓周长的 2%（允许的最大近似误差距离）
            # cv.arcLength(largest_contour, True)：计算并返回最大轮廓的周长，True 表示轮廓是闭合的
            epsilon = 0.02 * cv.arcLength(largest_contour, True)
            # 将复杂轮廓简化为多边形
            approx = cv.approxPolyDP(largest_contour, epsilon, True)
            
            # 检查简化后的轮廓，是否是四边形且面积足够大
            if len(approx) == 4 and area > 1000:
                if area > best_area:
                    # 如果大于已有的最大面积，就将当前面积设置为最大面积
                    best_area = area
                    # 选择面积最大的合格四边形，设置为最佳轮廓
                    # 重塑为 (4, 2) 的简洁格式
                    # approx 的原始形状：(4, 1, 2)
                    # approx = [
                    #     [[x1, y1]],  # 顶点 1
                    #     [[x2, y2]],  # 顶点 2
                    #     [[x3, y3]],  # 顶点 3
                    #     [[x4, y4]]   # 顶点 4
                    # ]
                    best_contour = approx.reshape(4, 2)
    
    # 调试模式下，如果检测到了四边形
    # debug：用户传入的调试标志 debug=debug
    if debug and best_contour is not None:
        # 绘制检测到的四边形
        # 创建调试图像副本
        debug_image = image.copy()
        # 绿色线条绘制四边形轮廓
        # reshape(-1, 1, 2)：将形状从(4, 2)变回 OpenCV 需要的(n, 1, 2)
        # -1：绘制所有轮廓
        cv.drawContours(debug_image, [best_contour.reshape(-1, 1, 2)], -1, (0, 255, 0), 3)
        for i, point in enumerate(best_contour):
            # 红色圆点标记顶点
            # tuple(point.astype(int))：将坐标转换为整数元组
            # -1：填充圆（实心）
            cv.circle(debug_image, tuple(point.astype(int)), 5, (0, 0, 255), -1)
            # 白色数字标注顶点序号
            # str(i)：顶点序号（0, 1, 2, 3）
            # cv.FONT_HERSHEY_SIMPLEX：字体类型
            # 0.8：字体大小
            cv.putText(debug_image, str(i), tuple(point.astype(int)), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        # 保存调试图片
        cv.imwrite("output/debug_detection.jpg", debug_image)
        print(f"调试图片已保存: output/debug_detection.jpg")
    
    # 输出：四边形的 4 个顶点坐标，或 None（未检测到）
    # best_contour = [
    #     [x1, y1],  # 顶点 1
    #     [x2, y2],  # 顶点 2
    #     [x3, y3],  # 顶点 3
    #     [x4, y4]   # 顶点 4
    # ]
    return best_contour


def detect_quadrilateral_by_edges(image, debug=False):
    """
    当颜色检测失败时，通过边缘检测寻找四边形
    基于图像梯度（边缘）而非颜色信息
    输出：四边形的 4 个顶点坐标，或 None（未检测到）
    """
    # 转换为灰度图，减少计算复杂度，只保留亮度信息
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # 高斯模糊，消除噪声干扰
    # sigmaX=0：会根据核大小自动计算标准差
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # Canny边缘检测
    # 50：低阈值，梯度值低于 50 的被认为是非边缘
    # 150：高阈值，梯度值高于 150 的被认为是强边缘
    # 介于 50-150 之间的像素根据连通性判断
    edges = cv.Canny(blurred, 50, 150)
    
    # 边缘优化：形态学操作
    kernel = np.ones((3, 3), np.uint8)
    # MORPH_CLOSE：闭运算，先膨胀后腐蚀，连接断开的边缘片段，填充边缘中的小间隙
    edges = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

    # NOTE: 以下内容同函数 detect_blue_quadrilateral()，写法略有差异
    # 查找所有外部轮廓
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None
    
    # 按面积排序
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    
    for contour in contours:
        # 近似轮廓为多边形
        epsilon = 0.02 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        
        # 检查是否是四边形
        if len(approx) == 4:
            # 检查四边形是否足够大
            area = cv.contourArea(approx)
            if area > 1000:
                if debug:
                    debug_image = image.copy()
                    cv.drawContours(debug_image, [approx], -1, (0, 255, 0), 3)
                    for i, point in enumerate(approx):
                        cv.circle(debug_image, tuple(point[0]), 5, (0, 0, 255), -1)
                    cv.imwrite("output/debug_edges.jpg", debug_image)
                    print(f"边缘检测调试图片已保存: output/debug_edges.jpg")
                
                return approx.reshape(4, 2)
    
    return None


def order_points(pts):
    """
    对四个点进行排序：左上，右上，右下，左下
    输入形状: (4, 2)
    pts = [
        [x1, y1],
        [x2, y2],
        [x3, y3],
        [x4, y4]
    ]
    """
    # 初始化坐标点
    rect = np.zeros((4, 2), dtype="float32")

    # 计算每个点的 x+y
    s = pts.sum(axis=1)
    # 左上点：x+y 最小
    rect[0] = pts[np.argmin(s)]
    # 右下点：x+y 最大
    rect[2] = pts[np.argmax(s)]

    # 计算每个点的 y-x
    diff = np.diff(pts, axis=1)
    # 右上点：y-x 最小
    rect[1] = pts[np.argmin(diff)]
    # 左下点：y-x 最大
    rect[3] = pts[np.argmax(diff)]
    
    # 输出形状: (4, 2)，标准化顺序
    # rect = [
    #     [x_tl, y_tl],  # 左上点
    #     [x_tr, y_tr],  # 右上点
    #     [x_br, y_br],  # 右下点
    #     [x_bl, y_bl]   # 左下点
    # ]
    return rect


def perspective_transform(image, src_points, target_width=314, target_height=100):
    """
    执行透视变换，将倾斜四边形转换为水平长方形
    输入：原始图像 + 四边形 4 个顶点 + 目标尺寸
    输出：校正后的水平长方形图像
    默认尺寸：314×100 像素
    """
    # 对源点进行排序
    src = order_points(src_points)
    
    # 定义目标点（水平长方形）
    dst = np.array([
        [0, 0],                                 # 左上点
        [target_width - 1, 0],                  # 右上点
        [target_width - 1, target_height - 1],  # 右下点
        [0, target_height - 1]                  # 左下点
    ], dtype="float32")
    
    # 计算透视变换矩阵
    # src和 dst 都必须是 4 个点，形状 (4, 2)
    matrix = cv.getPerspectiveTransform(src, dst)
    
    # 应用透视变换
    # (target_width, target_height)：输出图像尺寸
    warped = cv.warpPerspective(image, matrix, (target_width, target_height))
    
    # 输出：校正后的水平长方形图像
    return warped


def process_image(input_path, output_path, debug=False):
    """
    图片处理函数，协调各个检测和变换模块
    输入：输入图片路径、输出图片路径、调试标志
    输出：布尔值，表示处理是否成功
    """
    # 读取图片
    image = cv.imread(input_path)
    if image is None:
        print(f"无法读取图片: {input_path}")
        return False
    
    print(f"正在处理图片: {input_path}")
    print(f"原始图片尺寸: {image.shape}")
    
    # 确保输出目录存在
    # exist_ok=True：目录已存在时不报错，不做任何操作
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 首先尝试颜色检测
    blue_quad = detect_blue_quadrilateral(image, debug=debug)
    
    # 车牌颜色检测成功，不满足这个条件，没执行这部分代码
    if blue_quad is None:
        print("颜色检测未找到蓝色四边形，尝试边缘检测...")
        blue_quad = detect_quadrilateral_by_edges(image, debug=debug)
    
    if blue_quad is None:
        print("所有检测方法都未找到四边形")
        return False

    print(f"检测到四边形顶点: {blue_quad}")
    
    # 执行透视变换
    target_width = 314
    target_height = 100
    # 使用检测到的四边形顶点进行变换
    transformed = perspective_transform(image, blue_quad, target_width, target_height)
    
    print(f"变换后图片尺寸: {transformed.shape}")
    
    # 保存结果
    # cv.imwrite：返回布尔值表示保存是否成功
    success = cv.imwrite(output_path, transformed)
    
    # 根据保存结果返回相应的处理状态
    if success:
        print(f"处理完成，结果保存到: {output_path}")
        return True
    else:
        print(f"保存失败: {output_path}")
        return False


def main():
    """
    主函数
    """
    input_path = "images/car3_plat.jpg"
    output_path = "output/transformed_plate.jpg"
    
    # 处理图片（启用调试模式）
    # 调试模式下会生成中间结果图片，便于分析问题
    success = process_image(input_path, output_path, debug=True)
    
    if success:
        print("\n任务完成！")
        print(f"输入图片: {input_path}")
        print(f"输出图片: {output_path}")
        print(f"输出尺寸: 314x100 像素")
    else:
        print("\n处理失败，正在尝试手动指定四边形顶点...")
        # 如果自动检测失败，尝试手动指定（车牌检测成功，没有调用这个函数）
        try_manual_detection(input_path, output_path)


def try_manual_detection(input_path, output_path):
    """
    尝试手动指定四边形顶点
    当自动检测失败时，手动估计车牌位置
    """
    image = cv.imread(input_path)
    if image is None:
        print("无法读取图片进行手动处理")
        return
    
    # 根据常见车牌位置手动指定大致区域
    height, width = image.shape[:2]
    
    # 假设四边形大致在图片中央区域
    # 这里需要根据实际图片调整这些坐标，例如增加用户交互功能，让用户手动点击四个顶点
    manual_points = np.array([
        [width * 0.3, height * 0.4],  # 左上
        [width * 0.7, height * 0.4],  # 右上
        [width * 0.8, height * 0.6],  # 右下
        [width * 0.2, height * 0.6]   # 左下
    ], dtype="float32")
    
    print(f"使用手动指定顶点: {manual_points}")
    
    # 执行透视变换
    target_width = 314
    target_height = 100
    transformed = perspective_transform(image, manual_points, target_width, target_height)
    
    # 保存结果
    success = cv.imwrite(output_path, transformed)
    
    if success:
        print(f"手动处理完成，结果保存到: {output_path}")
    else:
        print("手动处理失败")


if __name__ == "__main__":
    # 调用主函数
    main()
