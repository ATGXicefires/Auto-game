import cv2
import numpy as np
import subprocess
import time
import os

# 獲取截圖存放的位置
def get_screenshot_path():
    return './src/modules/cache/screencap.png'

# 使用 ADB 截圖
def adb_screenshot():
    subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=open(get_screenshot_path(), 'wb'))
    
# 點擊畫面
def click_screen(x, y):
    subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)])

def calculate_and_tap_center(location, template_shape):
    """
    計算點擊位置的中心點並執行點擊操作。
    
    :param location: 圖片位置 (x, y)
    :param template_shape: 模板大小 (height, width)
    """
    button_center_x = location[0] + template_shape[1] // 2
    button_center_y = location[1] + template_shape[0] // 2
    subprocess.run(['adb', 'shell', 'input', 'tap', str(button_center_x), str(button_center_y)])

def calculate_and_tap_center(location, template_shape):
    """
    計算點擊位置的中心點並執行點擊操作。
    
    :param location: 圖片位置 (x, y)
    :param template_shape: 模板大小 (height, width)
    """
    button_center_x = location[0] + template_shape[1] // 2
    button_center_y = location[1] + template_shape[0] // 2
    subprocess.run(['adb', 'shell', 'input', 'tap', str(button_center_x), str(button_center_y)])

# 等待10秒直到某個圖像出現
def wait_10_until_image(image_path, confidence=0.9, timeout=10):
    start_time = time.time()  # 獲取當前時間
    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"無法讀取圖片: {image_path}")
        return None, None
    while time.time() - start_time < timeout:  # 當前時間 - 開始時間 < 超時時間
        try:
            adb_screenshot()
            screenshot = cv2.imread(get_screenshot_path(), cv2.IMREAD_COLOR)
            if screenshot is None:
                print("無法讀取截圖")
                return None, None
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"匹配值: {max_val}")  # 調試信息
            if max_val >= confidence:
                return max_loc, template.shape  # 如果找到圖像，返回其位置和模板大小
        except Exception as e:
            print(f"10_圖像識別中: {e}")  # 打印識別錯誤
        time.sleep(1)  # 等待1秒後再次嘗試
    return None, None  # 超過等待時間，返回 None