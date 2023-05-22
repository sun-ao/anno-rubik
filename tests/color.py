import numpy as np

cube_colors = {
    'white': [(240, 240, 240), (255, 255, 255)],
    'blue': [(0, 180, 240), (10, 200, 255)],
    'orange': [(230, 160, 0), (255, 210, 80)],
    'green': [(30, 190, 30), (70, 220, 80)],
    'yellow': [(240, 240, 0), (255, 255, 100)],
    'red': [(160, 20, 20), (200, 60, 60)]
}

def get_color_name(color):
    min_distance = float('inf')
    closest_color = None
    for color_name, (lower, upper) in cube_colors.items():
        distance = np.linalg.norm(np.array(color) - np.mean([np.array(lower), np.array(upper)], axis=0))
        if distance < min_distance:
            min_distance = distance
            closest_color = color_name
    return closest_color

# 测试
colors = [(254, 254, 254), (0, 189, 253), (255, 192, 37), (50, 203, 50), (254, 254, 0), (178, 34, 34)]

for color in colors:
    color_name = get_color_name(color)
    if color_name:
        print(f"Color: {color} is closest to {color_name}")
    else:
        print(f"Color: {color} is not recognized.")
