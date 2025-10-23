# 车牌透视变换项目

## 项目描述
使用Python和OpenCV自动检测图片中的倾斜蓝色四边形区域，并通过透视变换将其转换为水平的长方形区域。

## 功能特点
- 自动检测蓝色四边形区域
- 执行透视变换校正倾斜
- 输出指定尺寸（314x100像素）
- 去除黑色区域，保留蓝色内容

## 文件结构
```
project_plate10/
├── images/
│   └── car3_plat.jpg           # 输入图片
├── output/
│   ├── transformed_plate.jpg   # 处理后的输出图片
│   └── debug_detection.jpg     # 调试图片（显示检测到的四边形）
├── perspective_transform.py    # 处理脚本
├── verify_result.py            # 结果验证脚本
└── README.md                   # 项目说明文档
```

## 主要函数

**perspective_transform.py**

| 函数                            | 功能                                       |
| ------------------------------- | ------------------------------------------ |
| detect_blue_quadrilateral()     | 蓝色四边形检测函数                         |
| detect_quadrilateral_by_edges() | 通过边缘检测来检测四边形                   |
| order_points()                  | 对四个点进行排序：左上，右上，右下，左下   |
| perspective_transform()         | 执行透视变换，将倾斜四边形转换为水平长方形 |
| process_image()                 | 图片处理函数                               |
| main()                          | 主函数                                     |
| try_manual_detection()          | 尝试手动指定四边形顶点                     |

**verify_result.py**

| 函数                 | 功能                     |
| -------------------- | ------------------------ |
| verify_output()      | 验证输出图片是否符合要求 |
| check_blue_content() | 检查蓝色内容             |

## 处理流程

1. **颜色检测**：在HSV颜色空间中检测蓝色区域
2. **轮廓检测**：查找最大的蓝色四边形轮廓
3. **透视变换**：将倾斜四边形转换为水平长方形
4. **尺寸调整**：输出为314x100像素的图片
5. **结果验证**：检查输出尺寸和内容质量

## 使用方法

### 运行处理脚本
```bash
python improved_perspective_transform.py
```

### 验证结果
```bash
python verify_result.py
```

## 技术细节
- **颜色检测**：使用HSV颜色空间的多个蓝色范围进行检测
- **轮廓近似**：使用Douglas-Peucker算法近似多边形
- **透视变换**：使用OpenCV的getPerspectiveTransform和warpPerspective
- **尺寸控制**：精确控制输出为314x100像素

## 验证结果
- ✅ 输出尺寸：314x100像素
- ✅ 黑色区域：0.00%（无黑色区域）
- ✅ 蓝色区域：81.56%（显著的蓝色内容）

## 依赖库
- OpenCV (cv2)
- NumPy
- OS (Python标准库)

## 注意事项
- 脚本会自动创建output目录
- 包含调试功能，可生成检测过程的可视化图片
- 支持多种检测方法（颜色检测、边缘检测）
- 如果自动检测失败，会尝试手动指定区域
