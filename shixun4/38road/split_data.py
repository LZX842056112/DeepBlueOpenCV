import os
import shutil
import random

# ================= 配置区域 =================
# 你的原始图片和txt所在的文件夹路径
source_folder = r"./dataset"  # 例如: "C:/Users/Desktop/RoadData"
# 想要生成的标准数据集名称
dataset_name = "Road_Defect_Dataset"
# 训练集占比 (0.8 代表 80% 训练，20% 验证)
train_ratio = 0.8
# ===========================================

def split_dataset():
    # 创建 YOLO 目录结构
    base_dir = os.path.join(os.getcwd(), dataset_name)
    dirs = [
        f"{base_dir}/train/images", f"{base_dir}/train/labels",
        f"{base_dir}/val/images", f"{base_dir}/val/labels"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 获取所有图片文件
    files = [f for f in os.listdir(source_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
    random.shuffle(files) # 打乱顺序

    # 计算分割点
    split_index = int(len(files) * train_ratio)
    train_files = files[:split_index]
    val_files = files[split_index:]

    print(f"总文件: {len(files)} | 训练集: {len(train_files)} | 验证集: {len(val_files)}")

    # 移动文件的函数
    def copy_files(file_list, split_type):
        for file_name in file_list:
            base_name = os.path.splitext(file_name)[0]
            
            # 1. 复制图片
            src_img = os.path.join(source_folder, file_name)
            dst_img = os.path.join(base_dir, split_type, "images", file_name)
            shutil.copy(src_img, dst_img)

            # 2. 复制对应的txt (如果有的话)
            txt_name = base_name + ".txt"
            src_txt = os.path.join(source_folder, txt_name)
            if os.path.exists(src_txt):
                dst_txt = os.path.join(base_dir, split_type, "labels", txt_name)
                shutil.copy(src_txt, dst_txt)

    copy_files(train_files, "train")
    copy_files(val_files, "val")
    print(f"✅ 数据集已整理完成！保存在: {base_dir}")
    print("请记住这个路径，下一步要用。")

if __name__ == "__main__":
    split_dataset()