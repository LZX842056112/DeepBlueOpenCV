from ultralytics import YOLO

if __name__ == '__main__':
    # 1. 加载模型
    # 推荐使用 yolov8s.pt (Small版本)，比 Nano (n) 稍慢但对细小裂缝检测效果更好
    model = YOLO('yolov8s.pt')

    # 2. 开始训练
    model.train(
        data='road.yaml',  # 指向刚才创建的配置文件
        epochs=50,        # 训练 50 轮
        imgsz=640,         # 图片大小，如果裂缝很细看不清，可以尝试 1024
        batch=8,           # 显存小就设 4 或 8，显存大设 16
        name='road_experiment' # 结果保存的文件夹名字
    )