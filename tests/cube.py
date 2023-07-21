import cv2
import numpy as np
import json

# 魔方的颜色对应的BGR（蓝色、绿色、红色）值
brg_cube_colors = {
    'white': (255, 255, 255),
    'yellow': (0, 255, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'orange': (0, 165, 255),
    'red': (0, 0, 255)
}

# 魔方的颜色对应的HSV（色相、饱和度、明度）值
hsv_cube_colors = {
    'white': (0, 0, 255), 
    'yellow': (30, 255, 255),  
    'green': (60, 255, 255),  
    'blue': (120, 255, 255),  
    'orange': (10, 255, 255),  
    'red': (0, 255, 255)
}

# 调试 展示图片
def show_image(image, title):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# BGR值转换逻辑 （注意非RGB）
def rgb_to_hex(rgb):
    b, g, r = rgb
    hex_code = '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)
    return hex_code

# HSV颜色值转换为十六进制颜色代码
def hsv_to_hex(hsv):
    hsv_np = np.array([[hsv]], dtype=np.uint8)
    bgr_np = cv2.cvtColor(hsv_np, cv2.COLOR_HSV2BGR)
    return rgb_to_hex(bgr_np[0][0])

# 等比例缩放图片，最大高度不超过500
def preprocess_image(image):
    max_height = 500
    height, width = image.shape[:2]
    if height > max_height:
        scale_factor = max_height / height
        image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)))
    return image

# 旋转、倾斜的魔方，可以考虑使用透视变换
def warp_perspective(image, contour):
    # 获取轮廓的四个角点
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # 对角点进行排序（左上，右上，右下，左下）
    box_sorted = np.zeros_like(box)
    sum_pts = box.sum(axis=1)
    box_sorted[0] = box[np.argmin(sum_pts)]
    box_sorted[2] = box[np.argmax(sum_pts)]

    diff_pts = np.diff(box, axis=1)
    box_sorted[1] = box[np.argmin(diff_pts)]
    box_sorted[3] = box[np.argmax(diff_pts)]

    # 定义魔方的正方形面的目标点
    side_length = max([np.linalg.norm(box_sorted[0] - box_sorted[1]),
                       np.linalg.norm(box_sorted[1] - box_sorted[2]),
                       np.linalg.norm(box_sorted[2] - box_sorted[3]),
                       np.linalg.norm(box_sorted[3] - box_sorted[0])])
    
    dst_pts = np.array([[0, 0],
                        [side_length - 1, 0],
                        [side_length - 1, side_length - 1],
                        [0, side_length - 1]], dtype='float32')

    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(np.float32(box_sorted), dst_pts)

    # 执行透视变换
    warped = cv2.warpPerspective(image, M, (int(side_length), int(side_length)))

    return warped


def color_distance(color1, color2):
    # HSV色调通道是循环的，对于红色需要特别处理
    d_hue = min(abs(color1[0] - color2[0]), 180 - abs(color1[0] - color2[0]))
    d_sat = color1[1] - color2[1]
    d_val = color1[2] - color2[2]

    # 这里可以根据需要加权三个通道的距离，例如，对于色调通道加大权重
    distance = np.sqrt(d_hue**2 + d_sat**2 + d_val**2)
    return distance

def find_nearest_color(center_color):
    distances = {}
    for key, value in hsv_cube_colors.items():
        distance = color_distance(center_color, value)
        print(f"Distance between {center_color} and {key}: {distance}")
        #  if distance < 2000: 设定一个适当的阈值，需要根据实际情况调整
        distances[key] = distance

    if not distances:  # 如果所有颜色的距离都超过了阈值
        return None

    # 返回距离最小的颜色
    return min(distances, key=distances.get)

def extract_cube_colors(image):
    show_image(image, 'image')

    # 将图片转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_image(gray, 'gray')

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
    # 针对旋转，倾斜的魔方，可以考虑使用透视变换（效果不太好）
    # cropped_image = warp_perspective(image, max_contour)
    show_image(cropped_image, 'cropped_image')

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
            # center_color = cropped_image[center_y, center_x, :]
            # 提取区域的颜色平均值
            patch_size = 20
            patch_image = cropped_image[center_y - patch_size//2:center_y + patch_size//2, center_x - patch_size//2:center_x + patch_size//2, :]
            # show_image(patch_image, 'patch_image')

            # （1）RGB颜色识别，RGB对光线变化很敏感。注意配置 cube_colors 为 BGR 取值
            # center_color = np.mean(patch_image, axis=(0,1))
            # 将center_color转换为CSS可以使用的颜色编码
            # center_color_code = rgb_to_hex(center_color)
            # nearest_color = min(brg_cube_colors, key=lambda x: np.linalg.norm(center_color - brg_cube_colors[x]))
            
            # （2）HSV颜色识别，在提取颜色之前，将图像转换为HSV颜色空间。色调（Hue）通常更适合颜色识别，因为它对光线变化不太敏感。注意配置 cube_colors 为 HSV 取值
            hsv_image = cv2.cvtColor(patch_image, cv2.COLOR_BGR2HSV)
            # show_image(hsv_image, 'hsv_image')
            center_color = np.mean(hsv_image, axis=(0,1))
            center_color_code = hsv_to_hex(center_color)
            nearest_color = find_nearest_color(center_color)

            # 打印中心点的颜色
            print(f"Grid ({row+1}, {col+1}) - Center Color: {center_color}")
            print(f"Grid ({row+1}, {col+1}) - Nearest Color: {nearest_color}")

            # 将中心点的颜色和最接近的颜色存储到grid_colors列表中
            grid_colors.append({
                'center_color': center_color.tolist(),
                'nearest_color': nearest_color,
                'center_color_code': center_color_code
            })

            # 计算方框的位置和大小
            box_x = x + center_x - grid_size // 2
            box_y = y + center_y - grid_size // 2
            box_width = grid_size
            box_height = grid_size

            # 绘制方框
            cv2.rectangle(image, (box_x, box_y), (box_x + box_width, box_y + box_height), brg_cube_colors[nearest_color], 2)

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

def main():
    # 加载图片 - 本地图片
    image = cv2.imread('rubiks_cube.jpg')
    # image = cv2.imread('rubiks_cube_face.jpg')
    # image = cv2.imread('rubiks_cube_web.jpg')
    # image = cv2.imread('rubiks_cube_camera.jpg')
    # image = cv2.imread('rubiks_cube_colors.jpg')

    # 加载图片 - 线上图片
    # image_url = 'https://demo.sunao.cc/cube/white_face.jpg'
    # response = requests.get(image_url)
    # image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)

    # 图片预处理
    image = preprocess_image(image)

    # 提取魔方颜色
    extracted_image, grid_colors = extract_cube_colors(image)

    # 展示结果图片
    show_image(extracted_image, 'Rubik\'s Cube')

    # 将grid_colors以JSON格式输出
    print(json.dumps(grid_colors, indent=4))

if __name__ == '__main__':
    main()
