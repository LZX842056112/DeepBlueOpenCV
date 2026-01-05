import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import Dataset
import os
from PIL import Image


# --- 1. 模型定义 (保持不变) ---
class ResNetCatDog(nn.Module):
    def __init__(self, num_classes=2):
        super(ResNetCatDog, self).__init__()
        self.base_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        # 冻结参数
        for param in self.base_model.parameters():
            param.requires_grad = False
        in_features = self.base_model.fc.in_features
        self.base_model.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.base_model(x)


# --- 2. 优化后的 Dataset (懒加载) ---
class CatDogDataset(Dataset):
    def __init__(self, data_dir, mode='train', transform=None):
        self.data_dir = data_dir
        self.mode = mode
        self.transform = transform
        self.images_info = []  # 存储 (filename, label) 元组

        if not os.path.exists(data_dir):
            print(f"路径不存在: {data_dir}")
            return

        # 仅扫描文件名，不读取图片内容，速度极快
        files = os.listdir(data_dir)
        print(f"[{mode}] 正在扫描 {data_dir} 下的文件...")

        for fname in files:
            if not fname.lower().endswith(('.jpg', '.png', '.jpeg')):
                continue

            label = -1
            if mode == 'train':
                if 'cat' in fname.lower():
                    label = 0
                elif 'dog' in fname.lower():
                    label = 1
                else:
                    continue  # 训练模式跳过无标签图片

            # 存储路径和标签，而不是图片本身
            self.images_info.append((fname, label))

        print(f"[{mode}] 索引完成，共 {len(self.images_info)} 张图片")

    def __len__(self):
        return len(self.images_info)

    def __getitem__(self, idx):
        fname, label = self.images_info[idx]
        img_path = os.path.join(self.data_dir, fname)

        try:
            img = Image.open(img_path).convert('RGB')
            if self.transform:
                img = self.transform(img)

            # 如果是测试模式，我们可能需要在外部获取文件名，
            # 但为了保持 DataLoader 格式通用，通常这里只返回 data, target
            return img, label
        except Exception as e:
            # 遇到坏图，返回一个全0的tensor或者报错 (简单处理)
            print(f"Error loading {fname}: {e}")
            return torch.zeros((3, 224, 224)), label


def load_data(data_dir, mode='train', resize=(224, 224)):
    # 数据预处理
    transform = transforms.Compose([
        transforms.Resize(resize),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    dataset = CatDogDataset(data_dir, mode=mode, transform=transform)

    if len(dataset) == 0:
        return None if mode == 'train' else (None, None)

    if mode == 'test':
        # 提取文件名列表供 test.py 使用
        filenames = [info[0] for info in dataset.images_info]
        return dataset, filenames
    else:
        return dataset
