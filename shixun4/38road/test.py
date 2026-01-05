from ultralytics import YOLO
import os

# ================= 配置区域 =================
# 1. 你的模型路径 (刚才训练生成的 best.pt)
# 注意：如果路径里有中文或特殊符号，前面加 r，或者把 \ 改为 /
model_path = r'runs/detect/road_experiment/weights/best.pt'

# 2. 想要测试的图片文件夹路径
# 你可以用 val/images，或者找一个新的文件夹放一些网上的路面图
image_folder = r'test'


# ===========================================

def run_batch_test():
    print(f"🚀 开始加载模型: {model_path}...")
    model = YOLO(model_path)

    print(f"📂 正在读取文件夹: {image_folder}...")

    # 开始批量预测
    # save=True: 保存画了框的图片
    # conf=0.25: 置信度阈值 (低于0.25的框不显示，如果发现漏检多，可以调低到 0.15)
    # save_txt=True: 如果你需要把检测结果存成 txt 坐标文件，加上这个参数
    results = model.predict(source=image_folder, save=True, conf=0.15)

    print("\n✅ 测试完成！")
    # 打印结果保存的位置（YOLO会自动新建 predict, predict2... 文件夹）
    print(f"🖼️ 结果已保存在: {results[0].save_dir}")


if __name__ == '__main__':
    run_batch_test()
