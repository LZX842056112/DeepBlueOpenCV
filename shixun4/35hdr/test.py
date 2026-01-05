import torch
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from model import VGGSmall
from torch.utils.data import DataLoader

# 设置 Matplotlib 中文支持，防止标题乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 数据预处理 (必须与训练时保持完全一致，否则预测不准)
transform = transforms.Compose([
    transforms.Resize((32, 32)),  # 必须也是 32x32
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# 加载测试集
test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=10, shuffle=True)

# 初始化模型结构
model = VGGSmall().to(DEVICE)


def test_visual():
    try:
        # 加载训练好的权重
        # map_location=DEVICE: 确保在只有 CPU 的机器上也能加载 GPU 训练的模型
        model.load_state_dict(torch.load('mnist_vgg_fast.pth', map_location=DEVICE))
    except FileNotFoundError:
        print("未找到模型文件！请先运行 train.py")
        return

    model.eval()  # 切换到评估模式 (锁定 BatchNorm/Dropout)

    # 获取一个 Batch 的数据
    images, labels = next(iter(test_loader))
    images = images.to(DEVICE)

    # 推理时不计算梯度，节省显存和时间
    with torch.no_grad():
        output = model(images)
        # 获取概率最大的类别索引
        preds = output.argmax(dim=1)

    # 创建画布
    plt.figure(figsize=(12, 4))
    for i in range(5):  # 只画前 5 张
        ax = plt.subplot(1, 5, i + 1)

        # 处理图片以便显示：
        # 1. .cpu(): 从显存移回内存
        # 2. .squeeze(): 去掉单通道维度 (1, 32, 32) -> (32, 32)
        # 3. .numpy(): 转为 numpy 数组给 matplotlib 用
        img = images[i].cpu().squeeze().numpy()

        ax.imshow(img, cmap='gray')  # 用灰度图显示

        p = preds[i].item()  # 预测值
        t = labels[i].item()  # 真实值
        color = 'green' if p == t else 'red'  # 猜对了绿色，猜错了红色

        ax.set_title(f"预测:{p}\n真值:{t}", color=color)
        ax.axis('off')  # 不显示坐标轴

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    test_visual()