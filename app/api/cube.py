from flask import Blueprint, current_app, request, jsonify
import cv2
import numpy as np
import requests
import concurrent.futures
import kociemba
from qcloud_cos import CosConfig, CosS3Client
from datetime import datetime
import uuid

cube_bp = Blueprint('cube', __name__)

# 魔方的颜色对应的BGR值
cube_colors = {
    'white': (255, 255, 255),
    'blue': (255, 0, 0),
    'orange': (0, 165, 255),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'red': (0, 0, 255)
}

# BGR值转换逻辑 （注意非RGB）
def rgb_to_hex(rgb):
    b, g, r = rgb
    hex_code = '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)
    return hex_code


def preprocess_image(image):
    # 等比例缩放图片，最大高度不超过500
    max_height = 500
    height, width = image.shape[:2]
    if height > max_height:
        scale_factor = max_height / height
        image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)))
    return image

def extract_cube_colors(image):
    # 将图片转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 应用高斯模糊
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 边缘增强
    edges = cv2.Canny(blur, 50, 150)

    # 膨胀操作
    dilated = cv2.dilate(edges, None, iterations=2)

    # 查找轮廓
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

            # 将center_color转换为CSS可以使用的颜色编码
            center_color_code = rgb_to_hex((center_color[0], center_color[1], center_color[2]))

            # 根据颜色匹配最接近的颜色
            nearest_color = min(cube_colors, key=lambda x: np.linalg.norm(center_color - cube_colors[x]))

            # 将中心点的颜色和最接近的颜色存储到grid_colors列表中
            grid_colors.append({
                'center_color': center_color.tolist(),
                'center_color_code': center_color_code,
                'nearest_color': nearest_color,
                'nearest_color_code': rgb_to_hex(cube_colors[nearest_color])
            })

            # 绘制方框
            box_x = x + center_x - grid_size // 2
            box_y = y + center_y - grid_size // 2
            box_width = grid_size
            box_height = grid_size
            cv2.rectangle(image, (box_x, box_y), (box_x + box_width, box_y + box_height), cube_colors[nearest_color], 2)

            # 自适应字号
            font_scale = min(grid_size / 100, 1)
            font_thickness = max(int(grid_size / 150), 1)

            # 设置文本参数
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = nearest_color
            text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)

            # 计算文本位置
            text_x = int(box_x + (box_width - text_size[0]) / 2)
            text_y = int(box_y + (box_height + text_size[1]) / 2)

            # 绘制文本
            cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness, cv2.LINE_AA)

    return image, grid_colors

def process_image(image_url, index):
    try:
        response = requests.get(image_url)
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
        image = preprocess_image(image)
        processed_image, grid_colors = extract_cube_colors(image)
        result = {
            'index': index,
            'image_url': image_url,
            'grid_colors': grid_colors
        }
        return result
    except Exception as e:
        error_message = str(e)
        return {'index': index, 'image_url': image_url, 'error': error_message}

@cube_bp.route('/process_images', methods=['POST'])
def process_images():
    try:
        data = request.get_json()
        image_urls = data['image_urls']
        results = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i, image_url in enumerate(image_urls):
                future = executor.submit(process_image, image_url, i)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

        # 根据索引对结果进行排序
        results.sort(key=lambda x: x['index'])
        # 移除索引字段
        results = [{'image_url': r['image_url'], 'grid_colors': r['grid_colors']} for r in results]

        return jsonify(results)
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 500

@cube_bp.route('/process_upload', methods=['POST'])
def upload_file():
    try:
        # 获取上传的文件
        file = request.files['file']
        # 将文件读取为字节流
        file_bytes = file.read()
        # 备份文件至COS
        try:
            # 获取 COS 配置信息
            cos_region = current_app.config['COS_REGION']
            cos_secret_id = current_app.config['COS_SECRET_ID']
            cos_secret_key = current_app.config['COS_SECRET_KEY']
            cos_bucket_name = current_app.config['COS_BUCKET_NAME']

            # 初始化 COS 配置
            cos_config = CosConfig(Region=cos_region, SecretId=cos_secret_id, SecretKey=cos_secret_key)
            cos_client = CosS3Client(cos_config)

            if file:
                # 将文件上传至腾讯云 COS
                response = cos_client.put_object(
                    Bucket=cos_bucket_name,
                    Body=file_bytes,
                    Key=(datetime.now().strftime("%Y%m%d") + "/" + str(uuid.uuid4()) + "-" + file.filename)
                )
                # 返回上传结果
                print(response)
        except Exception as e:
            print(e)

        # 将字节流转换为 numpy 数组
        np_array = np.frombuffer(file_bytes, np.uint8)

        # 解码图像
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        image = preprocess_image(image)

        # 处理图像并提取颜色信息
        processed_image, grid_colors = extract_cube_colors(image)

        # 根据需要对颜色信息进行处理，比如保存到数据库、返回给前端等

        # 返回处理结果
        result = {
            'colors':  [item["nearest_color"] for item in grid_colors]
        }
        return jsonify(result)
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 500
    
@cube_bp.route('/solve_cube', methods=['POST'])
def solve_cube():
    try:
        data = request.get_json()
        cube_state = data['cube_state']

        # 使用 Kociemba 求解魔方
        solution = kociemba.solve(cube_state)

        return jsonify({'solution': solution})
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message}), 500