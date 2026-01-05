import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from model import ResNetCatDog, load_data

# 设置 Matplotlib 中文支持，防止标题乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载测试集
dataset_pack = load_data('./data/val', mode='test')
test_dataset, filenames = dataset_pack
test_loader = DataLoader(test_dataset, batch_size=5, shuffle=True)

# 初始化模型结构
model = ResNetCatDog().to(DEVICE)

def test_visual():
    try:
        # 加载训练好的权重
        # map_location=DEVICE: 确保在只有 CPU 的机器上也能加载 GPU 训练的模型
        model.load_state_dict(torch.load('cat_dog_resnet.pth', map_location=DEVICE))
    except FileNotFoundError:
        print("未找到模型文件！请先运行 train.py")
        return

    model.eval()

    # 获取一个 Batch 的数据
    images, _ = next(iter(test_loader))
    images_gpu = images.to(DEVICE)

    # 推理时不计算梯度，节省显存和时间
    with torch.no_grad():
        outputs = model(images_gpu)
        probs = torch.softmax(outputs, dim=1)
        preds = torch.argmax(probs, dim=1)

    # 创建画布
    plt.figure(figsize=(15, 5))
    class_names = ['Cat', 'Dog']
    batch_filenames = filenames[:5]

    for i in range(len(images)):
        ax = plt.subplot(1, 5, i + 1)

        # 反归一化
        img = images[i].permute(1, 2, 0).numpy()
        img = (img - img.min()) / (img.max() - img.min())

        ax.imshow(img)

        # 预测值
        pred_label = class_names[preds[i]]
        conf = probs[i][preds[i]].item() * 100
        fname = batch_filenames[i]

        ax.set_title(f"文件: {fname}\n预测: {pred_label}\n({conf:.1f}%)", color='blue', fontsize=10)
        ax.axis('off')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    test_visual()