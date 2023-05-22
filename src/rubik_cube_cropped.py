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

# 待处理的图片文件名列表
image_files = [
    './data/input/demo/blue_face.jpg',
    './data/input/demo/green_face.jpg',
    './data/input/demo/orange_face.jpg',
    './data/input/demo/red_face.jpg',
    './data/input/demo/white_face.jpg',
    './data/input/demo/yellow_face.jpg'
]

# 存储排序后的图片文件名列表
sorted_image_files = []

for file in image_files:
    # 加载图片
    image = cv2.imread(file)

    # 转换为灰度图像
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

    # 存储每个格子的颜色和位置
    grid_data = []

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

            # 存储颜色和位置
            grid_data.append((nearest_color, (left, top, right, bottom)))

    # 保存排序后的图片文件名和格子数据
    sorted_image_files.append((file, grid_data, cropped_image))

# 根据中间格子的颜色顺序，展示裁剪、标记颜色后的图片
display_order = ['white', 'blue', 'red', 'green', 'yellow', 'orange']

# 创建展示窗口
cv2.namedWindow('Cropped and Marked Images', cv2.WINDOW_NORMAL)

# 根据中间格子的颜色顺序，遍历排序后的图片文件和格子数据，展示图片
for color in display_order:
    for file, grid_data, cropped_image in sorted_image_files:
        # 查找中间格子的颜色
        middle_color = grid_data[4][0]

        # 如果中间格子的颜色与当前遍历的颜色一致，则显示该图片
        if middle_color == color:

            # 遍历格子数据，绘制方框和文本
            for grid_color, (left, top, right, bottom) in grid_data:
                # 绘制方框
                cv2.rectangle(cropped_image, (left, top), (right, bottom), cube_colors[grid_color], 2)

                # 设置文本参数
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_size, _ = cv2.getTextSize(grid_color, font, font_scale, font_thickness)

                # 计算文本位置
                text_x = int(left + (right - left) / 2 - text_size[0] / 2)
                text_y = int(top + (bottom - top) / 2 + text_size[1] / 2)

                # 绘制文本
                cv2.putText(cropped_image, grid_color, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness)

            # 显示图片
            cv2.imshow('Cropped and Marked Images', cropped_image)
            cv2.waitKey(0)

            # 打印输出每个格子提取的颜色值
            print(f"Image: {file}")
            for i, color in enumerate(grid_data):
                print(f"Grid {i+1}: {color}")
            print('----------------------')

# 关闭窗口
cv2.destroyAllWindows()
