import torch
import torch.nn as nn
import torch.optim as optim
from model import VGGSmall
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
# 引入混合精度训练所需的库 (Automatic Mixed Precision)
from torch.cuda.amp import autocast, GradScaler

# 【硬件加速优化】开启 CuDNN 自动调优
# 如果输入数据维度固定，这行代码能让显卡自动寻找最快的卷积算法
torch.backends.cudnn.benchmark = True

# 检查设备
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

# 数据预处理
transform = transforms.Compose([
    # 【速度权衡】Resize 到 32x32
    # 32 是 VGG 能处理的最小尺寸。相比 64x64，像素少了 75%，计算量大幅降低。
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# 加载数据集
# 【IO 加速优化】
# num_workers=4: 开启 4 个 CPU 子进程并行读取数据，防止 GPU 等待 CPU。
# pin_memory=True: 锁页内存，让数据从内存复制到显存的速度更快。
train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=4, pin_memory=True)

# 初始化模型并搬运到 GPU
model = VGGSmall().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 【AMP 优化】初始化梯度缩放器
# 混合精度训练可能会导致梯度数值太小而消失，Scaler 用于放大梯度，防止下溢。
scaler = GradScaler()


def train():
    epochs = 5
    print(f"开始训练，设备: {DEVICE}")

    for epoch in range(1, epochs + 1):
        # 切换到训练模式 (启用 Dropout/BatchNorm)
        model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            # non_blocking=True: 异步传输，允许 CPU 准备下一批数据时 GPU 不停顿
            data, target = data.to(DEVICE, non_blocking=True), target.to(DEVICE, non_blocking=True)
            # 清空上一步的残余梯度
            optimizer.zero_grad()

            # 【AMP 核心】开启混合精度上下文
            # 在这个 with 块内的计算 (前向传播) 会自动使用 float16 (半精度)，速度快且省显存
            with autocast():
                output = model(data)
                loss = criterion(output, target)

            # 【AMP 反向传播】
            # 1. 先将 loss 放大，防止 float16 梯度下溢变为 0
            # 2. .backward(): 计算梯度
            scaler.scale(loss).backward()

            # 3. 将梯度缩放回去并更新权重
            scaler.step(optimizer)

            # 4. 更新缩放因子，为下一次迭代做准备
            scaler.update()

            total_loss += loss.item()

            if batch_idx % 100 == 0:
                print(f"Epoch [{epoch}/{epochs}] Batch [{batch_idx}] Loss: {loss.item():.4f}")

        print(f"==> Epoch [{epoch}] Avg Loss: {total_loss / len(train_loader):.4f}")


if __name__ == '__main__':
    train()
    # 保存模型权重
    torch.save(model.state_dict(), 'mnist_vgg_fast.pth')
    print("模型已保存: mnist_vgg_fast.pth")
