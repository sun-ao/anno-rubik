from PIL import Image
import math
from collections import Counter

cube_colors = {
    'white': (255, 255, 255),
    'blue': (0, 0, 255),
    'orange': (255, 165, 0),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'red': (255, 0, 0)
}

image = Image.open('your_image.jpg')

grid_size = image.width // 3
num_rows = num_cols = 3

def color_distance(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)

def find_nearest_color(rgb_value):
    distances = []
    for color, cube_rgb_value in cube_colors.items():
        distance = color_distance(rgb_value, cube_rgb_value)
        distances.append((distance, color))
    distances.sort()
    return distances[0][1]

for row in range(num_rows):
    for col in range(num_cols):
        left = col * grid_size + grid_size // 2
        top = row * grid_size + grid_size // 2
        right = left + 1
        bottom = top + 1

        grid_color = image.getpixel((left, top))
        nearest_color = find_nearest_color(grid_color)
        
        print(f'Grid {row*num_cols + col + 1}: {nearest_color} ({grid_color})')
