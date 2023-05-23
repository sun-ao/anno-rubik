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
image = cv2.imread('your_image_camera.jpg')

# 划分图片为9个格子
rows, cols, _ = image.shape
grid_size = min(rows, cols) // 3

for row in range(3):
    for col in range(3):
        # 计算每个格子的区域
        top = row * grid_size
        bottom = (row + 1) * grid_size
        left = col * grid_size
        right = (col + 1) * grid_size

        # 提取格子的颜色
        grid_color = image[top:bottom, left:right, :]

        # 计算颜色的平均值
        avg_color = np.mean(np.mean(grid_color, axis=0), axis=0)

        # 根据颜色的平均值匹配最接近的颜色
        nearest_color = min(cube_colors, key=lambda x: np.linalg.norm(avg_color - cube_colors[x]))

        # 绘制方框和文本
        cv2.rectangle(image, (left, top), (right, bottom), cube_colors[nearest_color], 2)

        # 设置文本参数
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        text_size, _ = cv2.getTextSize(nearest_color, font, font_scale, font_thickness)

        # 计算文本位置
        text_x = int(left + (right - left) / 2 - text_size[0] / 2)
        text_y = int(top + (bottom - top) / 2 + text_size[1] / 2)

        # 绘制文本
        cv2.putText(image, nearest_color, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)

# 显示结果
cv2.imshow('Color Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
