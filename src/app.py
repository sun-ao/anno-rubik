from flask import Flask, request, jsonify
import cv2
import numpy as np
import json
import requests

app = Flask(__name__)

# 魔方的颜色对应的BGR值
cube_colors = {
    'white': (255, 255, 255),
    'blue': (255, 0, 0),
    'orange': (0, 165, 255),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'red': (0, 0, 255)
}

@app.route('/process_images', methods=['POST'])
def process_images():
    # 获取请求中的图片链接列表
    image_urls = request.json['image_urls']

    # 存储排序后的图片链接列表和格子数据
    sorted_images = []
    faces_data = []

    for url in image_urls:
        # 下载图片
        response = requests.get(url)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

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

        # 保存排序后的图片链接和格子数据
        sorted_images.append((url, grid_data, cropped_image))

        # 存储每个面的颜色数据
        face_data = {'image': url, 'grids': []}

        for i, (color, _) in enumerate(grid_data):
            face_data['grids'].append({'grid': i+1, 'color': color})

        faces_data.append(face_data)

    # 将每个面的颜色数据写入 JSON 文件
    # with open('faces_data.json', 'w') as json_file:
    #     json.dump(faces_data, json_file)

    return jsonify(faces_data)

if __name__ == '__main__':
    app.run()
