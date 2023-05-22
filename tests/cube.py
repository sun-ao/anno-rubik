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
image = cv2.imread('rubiks_cube.jpg')

# 将图片转换为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 应用阈值处理，将非白色区域设置为黑色
_, threshold = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

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
        # 计算每个格子的区域
        top = row * grid_size
        bottom = (row + 1) * grid_size
        left = col * grid_size
        right = (col + 1) * grid_size

        # 提取格子的颜色
        grid_color = cropped_image[top:bottom, left:right, :]

        # 计算颜色的平均值
        avg_color = np.mean(np.mean(grid_color, axis=0), axis=0)

        # 根据颜色的平均值匹配最接近的颜色
        nearest_color = min(cube_colors, key=lambda x: np.linalg.norm(avg_color - cube_colors[x]))

        # 绘制方框和文本
        cv2.rectangle(image, (left+x, top+y), (right+x, bottom+y), cube_colors[nearest_color], 2)

        # 设置文本参数
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        text_size, _ = cv2.getTextSize(nearest_color, font, font_scale, font_thickness)

        # 计算文本位置
        text_x = int(left + x + (right - left) / 2 - text_size[0] / 2)
        text_y = int(top + y + (bottom - top) / 2 + text_size[1] / 2)

        # 绘制文本
        cv2.putText(image, nearest_color, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)

        # 将颜色添加到列表中
        grid_colors.append(nearest_color)

# 将图片展示出来
cv2.imshow('Rubik\'s Cube', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 打印输出每个格子提取的颜色值
for i, color in enumerate(grid_colors):
    print(f"Grid {i+1}: {color}")
