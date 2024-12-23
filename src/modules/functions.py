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
    directory = os.path.dirname(json_path)
    
    # 確保目錄存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    default_settings = {
        "detect_mode": "Windows",
        "adb_ip_address": ""
    }
    
    # 如果文件不存在或為空，直接創建新文件
    if not os.path.exists(json_path) or os.stat(json_path).st_size == 0:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=4)
        print(f"初始化了 setting.json 文件: {json_path}")
    else:
        # 如果文件存在，檢查是否包含所需的鍵值
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                current_settings = json.load(f)
            
            # 檢查並添加缺失的鍵值
            is_modified = False
            for key in default_settings:
                if key not in current_settings:
                    current_settings[key] = default_settings[key]
                    is_modified = True
            
            # 如果有修改，保存更新後的設定
            if is_modified:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(current_settings, f, ensure_ascii=False, indent=4)
                print(f"更新了 setting.json 文件的缺失設定: {json_path}")
                
        except Exception as e:
            print(f"讀取或更新 setting.json 時發生錯誤: {str(e)}")
            # 如果發生錯誤，重新創建文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)
            print(f"重新創建了 setting.json 文件: {json_path}")
    
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
    
    # 從 setting.json 讀取已保存的 IP 地址
    setting_path = get_resource_path('cache/setting.json')
    saved_ip = None
    if os.path.exists(setting_path):
        with open(setting_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            saved_ip = settings.get('adb_ip_address')

    try:
        # 獲取當前所有連接的設備
        devices_output = subprocess.check_output('adb devices', shell=True).decode('utf-8')
        devices = [line.split()[0] for line in devices_output.splitlines() if 'device' in line]
        
        # 如果沒有找到任何設備，嘗試連接常用端口
        if not devices:
            default_ports = ['5555', '16384', '7555', '21503', '62001']
            for port in default_ports:
                try:
                    subprocess.check_output(
                        f'adb connect 127.0.0.1:{port}', 
                        shell=True, 
                        stderr=subprocess.STDOUT,
                        timeout=5
                    )
                except:
                    continue
            
            # 重新獲取設備列表
            devices_output = subprocess.check_output('adb devices', shell=True).decode('utf-8')
            devices = [line.split()[0] for line in devices_output.splitlines() if 'device' in line]

        if not devices:
            log_view.append_log("未找到可用的 ADB 設備")
            return None

        # 如果有已保存的 IP 且在可用設備列表中，將其放在列表最前面
        if saved_ip and saved_ip in devices:
            devices.remove(saved_ip)
            devices.insert(0, saved_ip)

        # 讓使用者選擇設備
        text, ok = QInputDialog.getItem(
            parent_widget,
            "選擇 ADB 設備",
            "請選擇要連接的 ADB 設備：",
            devices,
            0,  # 預設選擇第一項
            False  # 不允許編輯，只能選擇已檢測到的設備
        )

        if ok and text:
            try:
                # 嘗試連接選擇的設備
                output = subprocess.check_output(
                    f'adb connect {text}', 
                    shell=True, 
                    stderr=subprocess.STDOUT,
                    timeout=30
                )
                log_view.append_log(output.decode('utf-8'))

                # 確認連接是否成功
                if text in devices:
                    log_view.append_log(f"成功連接到 ADB: {text}")
                    selected_device_id = text

                    # 保存成功連接的設備到 setting.json
                    with open(setting_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    settings['adb_ip_address'] = text
                    with open(setting_path, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, ensure_ascii=False, indent=4)

                    return text
                else:
                    log_view.append_log(f"無法連接到 ADB: {text}")
                    return None

            except Exception as e:
                log_view.append_log(f"連接 ADB 時發生錯誤: {str(e)}")
                return None

    except Exception as e:
        log_view.append_log(f"檢測 ADB 設備時發生錯誤: {str(e)}")
        return None

    return None

# 獲取截圖存放的位置
def get_screenshot_path():
    return get_resource_path('cache/screenshot.png')

# 使用 ADB 截圖
def adb_screenshot():
    global selected_device_id
    if selected_device_id:
        with open(get_screenshot_path(), 'wb') as f:
            subprocess.run(
                ['adb', '-s', selected_device_id, 'exec-out', 'screencap', '-p'],
                stdout=f,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
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
    subprocess.run(
        ['adb', '-s', selected_device_id, 'shell', 'input', 'tap', str(button_center_x), str(button_center_y)],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

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

def initialize_connections_file():
    """初始化 connections.json 檔案"""
    json_path = get_resource_path('SaveData/connections.json')
    directory = os.path.dirname(json_path)
    
    # 確保目錄存在
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # 如果檔案不存在或為空，建立預設結構
    if not os.path.exists(json_path) or os.stat(json_path).st_size == 0:
        default_connections = {}  # 空字典作為預設值
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(default_connections, f, ensure_ascii=False, indent=4)
        print(f"初始化了 connections.json 檔案: {json_path}")
    else:
        # 如果檔案存在，確保它是有效的 JSON 格式
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json.load(f)  # 嘗試讀取 JSON
        except Exception as e:
            print(f"connections.json 格式無效，重新建立: {str(e)}")
            # 如果 JSON 無效，重新建立檔案
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)