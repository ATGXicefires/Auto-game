import os
import json
import sys
import pyautogui
import subprocess
import cv2
import numpy as np
from PIL import Image
import time
from log_view import LogView
from PySide6.QtWidgets import QMessageBox,QInputDialog

selected_device_id = None  # 全局變量來存儲選擇的設備 ID

def ensure_cache_directory():
    cache_path = get_resource_path('cache')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
        print(f"創建了新的緩存目錄: {cache_path}")
    else:
        print(f"緩存目錄已存在: {cache_path}")

def ensure_detect_directory():
    detect_path = get_resource_path('detect')
    if not os.path.exists(detect_path):
        os.makedirs(detect_path)
        print(f"創建了 detect 資料夾: {detect_path}")

def clear_sv_json():
    """清空 sv.json 文件"""
    sv_json_path = get_resource_path('SaveData/sv.json')
    if os.path.exists(sv_json_path):
        with open(sv_json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    else:
        print(f"文件不存在: {sv_json_path}")

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
    """獲取資源文件的絕對路徑，適用於打包後的環境"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

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
        location = match_template(image_path, log_view)
        if location:
            pyautogui.click(location, button='left')
            log_view.append_log(f"已點擊: {image_path}")
        else:
            log_view.append_log(f"未找到: {image_path}")

def match_template(template_path, log_view, confidence=0.9, timeout=30):
    """
    在螢幕截圖中尋找模板圖像的位置。
    
    :param template_path: 模板圖片的路徑
    :param log_view: 用於記錄日誌的 LogView 實例
    :param confidence: 匹配的信心值(預設0.9)
    :param timeout: 超時時間(預設30秒)
    :return: 匹配位置 (x, y) 或 None
    """
    if not os.path.exists(template_path):
        log_view.append_log(f"檔案不存在: {template_path}")
        return None

    def read_image_with_pil(image_path):
        try:
            pil_image = Image.open(image_path)
            return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            log_view.append_log(f"無法讀取影像: {e}")
            return None

    start_time = time.time()

    while time.time() - start_time < timeout:
        screenshot = pyautogui.screenshot()  # 截取螢幕
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # 將PIL格式轉為OpenCV格式
        template = read_image_with_pil(template_path)  # 使用 PIL 讀取模板圖像

        if template is None:
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
            log_view.append_log(f"找到匹配位置: {max_loc}, 匹配值: {max_val}, 中心點: ({center_x}, {center_y})")

            # 平滑移動鼠標到中心點並點擊
            pyautogui.moveTo(center_x, center_y, duration=0.5)  # duration 控制移動速度
            return (center_x, center_y)  # 返回匹配位置的中心點座標

        # 打印當前匹配的準確值
        log_view.append_log(f"當前匹配準確值：{max_val}")
        # 每秒檢測一次
        time.sleep(1)

    log_view.append_log("未找到匹配的影像")
    return None

def set_adb_connection(log_view, parent_widget):
    global selected_device_id
    ip_addresses = [
        "127.0.0.1:5555",
        "127.0.0.1:16384",
        "127.0.0.1:7555",
        "127.0.0.1:21503",
        "127.0.0.1:62001"
    ]

    max_attempts = 2

    for attempt in range(max_attempts):
        try:
            # 列出所有設備
            devices_output = subprocess.check_output('adb devices', shell=True).decode('utf-8')
            log_view.append_log(devices_output)

            # 解析設備列表
            devices = [line.split()[0] for line in devices_output.splitlines() if 'device' in line]
            if not devices:
                log_view.append_log("沒有找到可用的設備")
                continue

            # 優先選擇出現在 ip_addresses 的位址
            preferred_device_id = None
            for ip in ip_addresses:
                if ip in devices:
                    preferred_device_id = ip
                    break

            # 如果沒有找到優先設備，選擇第一個偵測到的設備
            if not preferred_device_id:
                preferred_device_id = devices[0]

            log_view.append_log(f"使用設備: {preferred_device_id}")

            # 移除其他設備
            for device in devices:
                if device != preferred_device_id:
                    subprocess.check_output(f'adb -s {device} disconnect', shell=True)
                    log_view.append_log(f"移除設備: {device}")

            # 設置選擇的設備 ID
            selected_device_id = preferred_device_id

            # 嘗試連接到優先設備
            for ip_address in ip_addresses:
                try:
                    output = subprocess.check_output(f'adb -s {preferred_device_id} connect {ip_address}', shell=True, stderr=subprocess.STDOUT, timeout=30)
                    log_view.append_log(output.decode('utf-8'))  # 記錄 ADB 連接的輸出訊息
                    log_view.append_log(f"成功連接到 ADB: {ip_address}")
                    return ip_address
                except subprocess.CalledProcessError as e:
                    log_view.append_log(f"連接 ADB 失敗: {e.output.decode('utf-8')}")
                except subprocess.TimeoutExpired:
                    log_view.append_log(f"連接 ADB 超時: {ip_address}")

        except Exception as e:
            log_view.append_log(f"獲取設備列表時出錯: {e}")

        # 如果所有 IP 地址都無法連接，詢問用戶是否要手動輸入
        reply = QMessageBox.question(
            parent_widget,
            "ADB 連接失敗",
            "無法連接到任何 ADB 位址。是否要手動輸入 ADB 位址？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 使用 QInputDialog 讓用戶輸入 ADB 地址
            text, ok = QInputDialog.getText(parent_widget, "手動輸入 ADB 地址", "請輸入 ADB 地址:")
            if ok and text:
                try:
                    output = subprocess.check_output(f'adb -s {preferred_device_id} connect {text}', shell=True, stderr=subprocess.STDOUT, timeout=30)
                    log_view.append_log(output.decode('utf-8'))  # 記錄 ADB 連接的輸出訊息
                    log_view.append_log(f"成功連接到 ADB: {text}")
                    selected_device_id = preferred_device_id
                    return text
                except subprocess.CalledProcessError as e:
                    log_view.append_log(f"連接 ADB 失敗: {e.output.decode('utf-8')}")
                except subprocess.TimeoutExpired:
                    log_view.append_log(f"連接 ADB 超時: {text}")

    log_view.append_log("ADB 連接出現預期外的問題")
    print("ADB 連接出現預期外的問題")
    return None

# 獲取截圖存放的位置
def get_screenshot_path():
    return get_resource_path('cache/screenshot.png')

# 使用 ADB 截圖
def adb_screenshot():
    global selected_device_id
    if selected_device_id:
        subprocess.run(['adb', '-s', selected_device_id, 'exec-out', 'screencap', '-p'], stdout=open(get_screenshot_path(), 'wb'))
    else:
        print("未選擇設備，無法截圖")

def ADB_calculate_and_tap_center(location, template_shape, log_view):
    """
    計算點擊位置的中心點並執行點擊操作。
    
    :param location: 圖片位置 (x, y)
    :param template_shape: 模板大小 (height, width)
    """
    global selected_device_id
    if not selected_device_id:
        log_view.append_log("未選擇設備，無法進行點擊操作")
        return

    button_center_x = location[0] + template_shape[1] // 2
    button_center_y = location[1] + template_shape[0] // 2
    subprocess.run(['adb', '-s', selected_device_id, 'shell', 'input', 'tap', str(button_center_x), str(button_center_y)])

def ADB_match_template(step_array, log_view, confidence=0.9, timeout=30):
    global selected_device_id
    if not selected_device_id:
        log_view.append_log("未選擇設備，無法進行模板匹配")
        return None, None

    for template_path in step_array:
        # 確保 template_path 是一個有效的相對路徑
        if template_path.startswith('_internal\\'):
            template_path = template_path[len('_internal\\'):]

        full_template_path = get_resource_path(template_path)
        if not os.path.exists(full_template_path):
            log_view.append_log(f"模板文件不存在: {full_template_path}")
            continue

        start_time = time.time()  # 獲取當前時間

        # 使用 PIL 讀取圖片，然後轉換為 OpenCV 格式
        try:
            pil_image = Image.open(full_template_path)
            template = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            log_view.append_log(f"無法讀取圖片: {full_template_path}, 錯誤: {e}")
            continue

        while time.time() - start_time < timeout:  # 當前時間 - 開始時間 < 超時時間
            try:
                adb_screenshot()
                screenshot = cv2.imread(get_screenshot_path(), cv2.IMREAD_COLOR)
                if screenshot is None:
                    log_view.append_log("無法讀取截圖")
                    continue

                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                log_view.append_log(f"匹配值: {max_val}")

                if max_val >= confidence:
                    log_view.append_log(f"找到匹配位置: {max_loc}")
                    return max_loc, template.shape  # 返回位置和模板大小
            except Exception as e:
                log_view.append_log(f"圖像識別中: {e}")  # 打印識別錯誤

            time.sleep(1)  # 等待1秒後再次嘗試

    log_view.append_log("未找到匹配的影像")
    return None, None  # 超過等待時間，返回 None

def ADB_Click_step_by_step(step_array, log_view):
    # 依序尋找並使用 ADB 點擊每個 Step[Y] 對應的圖片
    for image_path in step_array:
        log_view.append_log(f"正在尋找並點擊: {image_path}")
        location, template_shape = ADB_match_template([image_path], log_view)
        if location:
            ADB_calculate_and_tap_center(location, template_shape, log_view)
            log_view.append_log(f"已點擊: {image_path}")
        else:
            log_view.append_log(f"未找到: {image_path}")