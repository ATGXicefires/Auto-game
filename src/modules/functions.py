import os
import json
import sys
import pyautogui
import cv2
import numpy as np
from PIL import Image
import time

def ensure_cache_directory():
    cache_path = get_resource_path('cache')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
        print(f"創建了 cache 資料夾: {cache_path}")

def ensure_detect_directory():
    detect_path = get_resource_path('detect')
    if not os.path.exists(detect_path):
        os.makedirs(detect_path)
        print(f"創建了 detect 資料夾: {detect_path}")

def clear_sv_json():
    """清空 sv.json 文件"""
    json_path = get_resource_path("SaveData/sv.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)
    print(f"Cleared {json_path}")

def ensure_sv_json():
    json_path = get_resource_path('SaveData/sv.json')
    directory = os.path.dirname(json_path)
    if not os.path.exists(directory):
        os.makedirs(directory)  # 確保目錄存在
    if not os.path.exists(json_path):
        # 創建一個空的 JSON 文件 
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        print(f"創建了 sv.json 文件: {json_path}")

def initialize_setting_file():
    json_path = get_resource_path('cache/setting.json')
    if not os.path.exists(json_path) or os.stat(json_path).st_size == 0:
        # 初始化 setting.json 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"detect_mode": "Windows"}, f, ensure_ascii=False, indent=4)
        print(f"初始化了 setting.json 文件: {json_path}")
    return json_path

def get_resource_path(relative_path):
    """獲取資源文件的正確路徑"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_json_variables(file_path):
    '''
    從指定的 JSON 檔案中讀取變數並返回為字典。
    
    參數:
    file_path: JSON 檔案的路徑
    
    返回:
    包含 JSON 內容的字典
    '''
    full_path = get_resource_path(file_path)

    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return data

def get_max_step_value(json_data):
    '''
    從 JSON 資料中找出 "Step[Y]" 的最大 Y 值。
    
    參數:
    json_data: 包含 JSON 內容的字典
    
    返回:
    最大的 Y 值
    '''
    max_step = 0
    for key in json_data.keys():
        if key.startswith("Step["):
            # 提取 Y 值
            try:
                y_value = int(key.split('[')[1].split(']')[0])
                if y_value > max_step:
                    max_step = y_value
            except ValueError:
                continue
    return max_step

def Click_step_by_step(step_array, log_view):
    # 依序尋找並點擊每個 Step[Y] 對應的圖片
    for image_path in step_array:
        log_view.append_log(f"正在尋找並點擊: {image_path}")
        location = match_template(image_path)
        if location:
            pyautogui.click(location, button='left')
            log_view.append_log(f"已點擊: {image_path}")
        else:
            log_view.append_log(f"未找到: {image_path}")

def match_template(template_path, confidence=0.9, timeout=10, log_view=None):
    """
    在螢幕截圖中尋找模板圖像的位置。
    
    :param template_path: 模板圖片的路徑
    :param confidence: 匹配的信心值(預設0.9)
    :param timeout: 超時時間(預設10秒)
    :return: 匹配位置 (x, y) 或 None
    """
    if not os.path.exists(template_path):
        if log_view:
            log_view.append_log(f"檔案不存在: {template_path}")
        return None

    def read_image_with_pil(image_path):
        try:
            pil_image = Image.open(image_path)
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            if log_view:
                log_view.append_log(f"無法讀取影像: {e}")
            return None

    start_time = time.time()

    while time.time() - start_time < timeout:
        screenshot = pyautogui.screenshot()  # 截取螢幕
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # 將PIL格式轉為OpenCV格式
        template = read_image_with_pil(template_path)  # 使用 PIL 讀取模板圖像

        if template is None:
            if log_view:
                log_view.append_log("無法讀取模板圖片")
            return None

        # 執行模板匹配
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 檢查匹配度是否符合要求
        if max_val >= confidence:
            # 計算匹配位置的中心點
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2
            if log_view:
                log_view.append_log(f"找到匹配位置: {max_loc}, 匹配值: {max_val}, 中心點: ({center_x}, {center_y})")

            # 平滑移動鼠標到中心點並點擊
            pyautogui.moveTo(center_x, center_y, duration=0.5)  # duration 控制移動速度
            pyautogui.click()
            return (center_x, center_y)  # 返回匹配位置的中心點座標

        # 打印當前匹配的準確值
        if log_view:
            log_view.append_log(f"當前匹配準確值：{max_val}")
        # 每秒檢測一次
        time.sleep(1)

    if log_view:
        log_view.append_log("未找到匹配的影像")
    return None

# 其他函數如 match_template 等可以在這裡定義或在其他模塊中定義並導入