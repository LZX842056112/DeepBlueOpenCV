import torch.nn as nn
from torchvision import models


class VGGSmall(nn.Module):
    def __init__(self, num_classes=10):
        super(VGGSmall, self).__init__()

        # 1. 加载官方 VGG11_BN 模型
        # weights=None: 不下载预训练权重（因为我们要改结构且跑 MNIST，从头训练更快）
        # _bn: 使用带 BatchNormalization 的版本，训练收敛速度比普通 VGG 快很多
        self.vgg = models.vgg11_bn(weights=None)

        # 2. 修改第一层卷积 (适配单通道输入)
        # 获取原始 VGG 的第一层卷积结构
        old_layer = self.vgg.features[0]
        # 创建一个新的卷积层，保留原来的参数（核大小、步长），但把输入通道改为 1 (灰度图)
        self.vgg.features[0] = nn.Conv2d(
            in_channels=1,  # MNIST 是单通道灰度图
            out_channels=old_layer.out_channels,
            kernel_size=old_layer.kernel_size,
            stride=old_layer.stride,
            padding=old_layer.padding
        )

        # 3. 【极速优化点】移除 AvgPool 层
        # 原生 VGG 在进入分类器前，会将特征图强制池化到 7x7。
        # 但我们的输入只有 32x32，经过 5 次下采样后已经是 1x1 了。
        # 如果强制用 AvgPool，会浪费计算资源。Identity() 表示“什么都不做”，直接跳过。
        self.vgg.avgpool = nn.Identity()

        # 4. 【极速优化点】重构分类器 (大幅减少参数)
        # 原生 VGG 分类器有 3 层全连接：4096 -> 4096 -> 1000 (参数量上亿，极大拖慢速度)
        # 我们改成单层全连接：512 -> 10 (参数量仅 5000+，速度提升巨大)
        self.vgg.classifier = nn.Sequential(
            nn.Flatten(),  # 将特征图展平成一维向量
            nn.Linear(512, num_classes)  # 直接映射到 10 个类别
        )

    def forward(self, x):
        # 数据流向：features -> avgpool(跳过) -> classifier
        return self.vgg(x)
