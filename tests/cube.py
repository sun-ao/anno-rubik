import cv2
import numpy as np

# 魔方的颜色对应的BGR值
cube_colors = {
    'white': (255, 255, 255),
    'blue': (255, 0, 0),
    'orange': (0, 165, 255),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'red': (0, 0, 255)
}

# 加载图片
image = cv2.imread('../data/input/camera/red.jpg')

# 将图片转换为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 自适应阈值处理，提取魔方面的区域
threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 4)

# 查找轮廓
contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 确定最大轮廓
max_contour = max(contours, key=cv2.contourArea)

# 计算最大轮廓的边界框
x, y, w, h = cv2.boundingRect(max_contour)

# 裁剪图片，只保留魔方的这个面
cropped_image = image[y:y+h, x:x+w]

# 划分裁剪后的图片为9个格子
rows, cols, _ = cropped_image.shape
grid_size = min(rows, cols) // 3

# 创建一个空列表用于存储每个格子的颜色值
grid_colors = []

for row in range(3):
    for col in range(3):
        # 计算每个格子的中心点坐标
        center_x = int((col + 0.5) * grid_size)
        center_y = int((row + 0.5) * grid_size)

        # 提取中心点的颜色
        center_color = cropped_image[center_y, center_x, :]

        # 打印中心点的颜色
        print(f"Grid ({row+1}, {col+1}) - Center Color: {center_color}")

        # 根据颜色匹配最接近的颜色
        nearest_color = min(cube_colors, key=lambda x: np.linalg.norm(center_color - cube_colors[x]))

        # 绘制方框和文本
        cv2.rectangle(image, (x + center_x - grid_size // 2, y + center_y - grid_size // 2),
                      (x + center_x + grid_size // 2, y + center_y + grid_size // 2),
                      cube_colors[nearest_color], 2)

        # 设置文本参数
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        text_size, _ = cv2.getTextSize(nearest_color, font, font_scale, font_thickness)

        # 计算文本位置
        text_x = int(x + center_x - text_size[0] / 2)
        text_y = int(y + center_y + text_size[1] / 2)

        # 绘制文本
        cv2.putText(image, nearest_color, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)

# 展示结果图片
cv2.imshow('Rubik\'s Cube Extraction', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
