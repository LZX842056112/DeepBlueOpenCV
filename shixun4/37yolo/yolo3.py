import cv2
import numpy as np


def yolo_v3_car_tracking(video_path, output_path):
    # 定义 YOLOv3 模型文件的路径
    # weights_path: 模型的权重文件，包含训练好的参数
    weights_path = "./yolo-coco/yolov3.weights"
    # config_path: 模型的配置文件，包含网络结构定义
    config_path = "./yolo-coco/yolov3.cfg"
    # names_path: 类别名称文件，包含 COCO 数据集的 80 个类别名
    names_path = "./yolo-coco/coco.names"

    print("正在加载 YOLOv3 模型...")
    # 使用 OpenCV 的 DNN 模块加载 Darknet 框架训练的模型
    # 这一步会将模型结构和权重加载到内存中
    net = cv2.dnn.readNet(weights_path, config_path)

    # 设置计算后台为 OpenCV 默认实现
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    # 设置计算目标为 CPU (因为标准版 OpenCV 不支持 NVIDIA GPU 加速)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    with open(names_path, "r") as f:
        # 逐行读取文件，并去除每行末尾的换行符，存入 classes 列表
        classes = [line.strip() for line in f.readlines()]

    # 获取网络所有层的名称
    layer_names = net.getLayerNames()
    # 获取输出层的索引 (YOLOv3 有 3 个尺度的输出层)
    out_layers = net.getUnconnectedOutLayers()

    # 根据 OpenCV 版本的不同，out_layers 返回的格式可能不同
    # 如果返回的是一维数组 (OpenCV 新版本)，直接减 1 获取索引
    if len(out_layers.shape) == 1:
        output_layers = [layer_names[i - 1] for i in out_layers]
    # 如果返回的是二维数组 (OpenCV 旧版本)，取第一个元素再减 1
    else:
        output_layers = [layer_names[i[0] - 1] for i in out_layers]

    # 打开输入视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频: {video_path}")
        return

    # 获取视频的宽度 (像素)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # 获取视频的高度 (像素)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 获取视频的帧率 (FPS)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 初始化视频写入器对象，用于保存处理后的视频
    # 参数: 输出路径, 编码格式(mp4v), 帧率, 分辨率
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    print("开始处理视频 (按 'q' 退出)...")

    # 使用 try-finally 结构确保即使程序出错也能正确释放资源
    try:
        while True:
            # 逐帧读取视频
            # ret: 布尔值，表示是否读取成功
            # frame: 当前帧的图像数据 (NumPy 数组)
            ret, frame = cap.read()

            # 如果没读到帧 (视频结束)，跳出循环
            if not ret:
                break

            # 获取当前帧的高度和宽度 (用于后续坐标还原)
            h_curr, w_curr = frame.shape[:2]

            # --- 图像预处理 ---
            # blobFromImage 将图像转换为神经网络的输入格式 (Blob)
            # 1/255.0: 归一化，将像素值缩放到 [0, 1]
            # (416, 416): YOLOv3 要求的输入尺寸，会进行缩放
            # (0, 0, 0): 均值减法的值，这里不减
            # swapRB=True: OpenCV 读入是 BGR，YOLO 需要 RGB，所以要交换通道
            # crop=False: 不裁剪，进行缩放
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), (0, 0, 0), swapRB=True, crop=False)

            # 将处理好的 Blob 设置为网络的输入
            net.setInput(blob)

            # --- 推理 (Forward Pass) ---
            # 运行前向传播，计算输出层的返回值
            # outs 是一个列表，包含 3 个尺度的检测结果
            outs = net.forward(output_layers)

            # 初始化列表，用于存储筛选后的检测结果
            class_ids = []  # 存储类别 ID
            confidences = []  # 存储置信度
            boxes = []  # 存储边界框坐标

            # 遍历每个输出层的结果
            for out_data in outs:
                # 遍历每个检测框
                for detection in out_data:
                    # detection 前 5 个值是 [x, y, w, h, objectness]
                    # 后面的值是各个类别的概率
                    scores = detection[5:]

                    # 找到概率最大的类别 ID
                    class_id = np.argmax(scores)
                    # 获取该类别的置信度
                    confidence = scores[class_id]

                    # --- 过滤逻辑 ---
                    # 1. 置信度 > 0.5 (过滤掉把握不大的检测)
                    # 2. 类别必须是 2(轿车), 5(巴士), 7(卡车)
                    if confidence > 0.5 and class_id in [2, 5, 7]:
                        # detection 中的坐标是归一化的 (0-1)，需要乘以原图宽高还原
                        center_x = int(detection[0] * w_curr)  # 中心点 X
                        center_y = int(detection[1] * h_curr)  # 中心点 Y
                        w = int(detection[2] * w_curr)  # 宽度
                        h = int(detection[3] * h_curr)  # 高度

                        # 计算矩形框左上角的坐标 (OpenCV 画图需要左上角坐标)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        # 将结果存入列表
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # --- 非极大值抑制 (NMS) ---
            # 这一步用于去除对同一个物体重复检测的框
            # 0.5: 置信度阈值 (虽然前面过滤过，这里再传一次)
            # 0.4: NMS 阈值 (IoU 阈值)，如果两个框重叠度超过 0.4，则去掉置信度较低的那个
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # 如果检测到了物体
            if len(indexes) > 0:
                # 遍历保留下来的框的索引
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]  # 获取坐标
                    label = classes[class_ids[i]]  # 获取类别名称
                    conf = confidences[i]  # 获取置信度

                    # --- 绘制结果 ---
                    color = (0, 255, 0)  # 定义框的颜色 (绿色)

                    # 在原图上画矩形框
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

                    # 准备标签文本
                    text = f"{label} {conf:.2f}"

                    # 获取文本的尺寸，用于画背景框
                    (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                    # 画文字背景 (实心矩形)，让文字更清晰
                    cv2.rectangle(frame, (x, y - text_h - 10), (x + text_w, y), color, -1)

                    # 在背景上写字
                    cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # 将绘制好结果的帧写入输出视频
            out.write(frame)

            # 在窗口中实时显示处理结果
            cv2.imshow("YOLOv3 Car Detection", frame)

            # 按 'q' 键退出循环 (1ms 延时)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 捕获键盘中断异常 (Ctrl+C)
    except KeyboardInterrupt:
        print("停止")

    # finally 块确保无论如何都会执行资源释放
    finally:
        cap.release()  # 释放视频读取对象
        out.release()  # 释放视频写入对象 (这一步很重要，否则视频文件会损坏)
        cv2.destroyAllWindows()  # 关闭所有 OpenCV 窗口
        print(f"完成: {output_path}")


# 程序入口
if __name__ == "__main__":
    yolo_v3_car_tracking("./input/test_1.mp4", "./output/output_yolo3.mp4")
