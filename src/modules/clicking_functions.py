import cv2
import numpy as np
import pyautogui
import time
from PIL import Image
import os
import subprocess
import json
from functions import get_resource_path

def load_steps_from_json(json_path):
    """
    從指定的 JSON 檔案讀取步驟資訊
    
    Args:
        json_path (str): JSON 檔案的完整路徑
        
    Returns:
        tuple: (步驟列表, 最大步數)
    """
    try:
        json_path = get_resource_path(json_path)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if 'steps' not in data:
            return [], 0
            
        steps_dict = data['steps']
        steps_array = []
        max_steps = 0
        
        i = 1
        while f"Step{i}" in steps_dict:
            step_data = steps_dict[f"Step{i}"]
            
            # 處理新舊格式相容性
            if isinstance(step_data, str):
                steps_array.append({
                    'location': step_data,
                    'timeout': 30
                })
            else:
                steps_array.append({
                    'location': step_data.get('location', ''),
                    'timeout': step_data.get('timeout', 30)
                })
                
            max_steps = i
            i += 1
            
        return steps_array, max_steps
        
    except Exception as e:
        print(f"讀取 JSON 檔案時發生錯誤: {str(e)}")
        return [], 0

def ADB_screenshot():
    """
    使用 ADB 截取螢幕畫面
    
    Returns:
        numpy.ndarray: OpenCV 格式的圖片
    """
    try:
        # 使用 ADB 截圖並保存到手機
        subprocess.run('adb shell screencap -p /sdcard/screenshot.png', shell=True, check=True)
        # 將截圖從手機拉到電腦
        subprocess.run('adb pull /sdcard/screenshot.png temp_screenshot.png', shell=True, check=True)
        # 刪除手機上的截圖
        subprocess.run('adb shell rm /sdcard/screenshot.png', shell=True, check=True)
        
        # 讀取截圖
        screenshot = cv2.imread('temp_screenshot.png')
        # 刪除臨時檔案
        os.remove('temp_screenshot.png')
        
        return screenshot
    except Exception as e:
        print(f"ADB 截圖時發生錯誤: {str(e)}")
        return None

def ADB_click(x, y):
    """
    使用 ADB 在指定座標點擊
    
    Args:
        x (int): X 座標
        y (int): Y 座標
    """
    try:
        subprocess.run(f'adb shell input tap {x} {y}', shell=True, check=True)
        return True
    except Exception as e:
        print(f"ADB 點擊時發生錯誤: {str(e)}")
        return False

def detect_and_click_image(template_path, log_view, confidence=0.9, timeout=30, is_adb_mode=False):
    """
    在螢幕上偵測圖片並點擊
    
    Args:
        template_path (str): 模板圖片路徑
        log_view: 日誌視圖實例
        confidence (float): 匹配信心值
        timeout (int): 超時時間(秒)
        is_adb_mode (bool): 是否使用 ADB 模式
    
    Returns:
        tuple or None: 如果找到圖片則返回座標，否則返回 None
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
    log_view.append_log(f"開始尋找圖片，超時時間設定為 {timeout} 秒")

    while time.time() - start_time < timeout:
        if is_adb_mode:
            # 使用 ADB 截圖
            screenshot = ADB_screenshot()
            if screenshot is None:
                log_view.append_log("ADB 截圖失敗")
                return None
            # 使用 PyAutoGUI 截圖
        else:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        template = read_image_with_pil(template_path)
        if template is None:
            log_view.append_log("無法讀取模板圖片")
        # 執行模板匹配
            return None

        # 檢查匹配度是否符合要求
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            template_height, template_width = template.shape[:2]
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2
            log_view.append_log(f"找到匹配位置: {max_loc}, 匹配值: {max_val}, 中心點: ({center_x}, {center_y})")

            if is_adb_mode:
                if ADB_click(center_x, center_y):
                    log_view.append_log("ADB 點擊成功")
                else:
                    log_view.append_log("ADB 點擊失敗")
                    return None
            else:
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                pyautogui.click()

            return (center_x, center_y)

        log_view.append_log(f"當前匹配準確值：{max_val}，剩餘時間：{int(timeout - (time.time() - start_time))}秒")
        time.sleep(1)

    log_view.append_log(f"超過設定的 {timeout} 秒仍未找到匹配的影像")
    return None

def Click_step_by_step(step_array, log_view):
    """
    依序執行 Windows 模式的點擊操作
    
    Returns:
        tuple: (是否成功完成所有步驟, 當前執行到第幾步)
    """
    total_steps = len(step_array)
    for current_step, step in enumerate(step_array, 1):
        template_path = get_resource_path(step['location'])
        timeout = step['timeout']  # 使用步驟特定的 timeout 設定
        log_view.append_log(f"正在執行第 {current_step}/{total_steps} 步: {step['location']} (超時設定: {timeout}秒)")
        
        result = detect_and_click_image(
            template_path, 
            log_view, 
            timeout=timeout,  # 傳遞 timeout 設定
            is_adb_mode=False
        )
        
        if result is None:
            log_view.append_log(f"步驟 {current_step} 失敗: 無法找到或點擊 {step['location']}")
            return False, current_step
            
        log_view.append_log(f"步驟 {current_step} 完成")
        time.sleep(1)
    
    return True, total_steps

def ADB_Click_step_by_step(step_array, log_view):
    """
    依序執行 ADB 模式的點擊操作
    
    Returns:
        tuple: (是否成功完成所有步驟, 當前執行到第幾步)
    """
    total_steps = len(step_array)
    for current_step, step in enumerate(step_array, 1):
        template_path = get_resource_path(step['location'])
        timeout = step['timeout']  # 使用步驟特定的 timeout 設定
        log_view.append_log(f"正在執行第 {current_step}/{total_steps} 步: {step['location']} (超時設定: {timeout}秒)")
        
        result = detect_and_click_image(
            template_path, 
            log_view, 
            timeout=timeout,  # 傳遞 timeout 設定
            is_adb_mode=True
        )
        
        if result is None:
            log_view.append_log(f"步驟 {current_step} 失敗: 無法找到或點擊 {step['location']}")
            return False, current_step
            
        log_view.append_log(f"步驟 {current_step} 完成")
        time.sleep(1)
    
    return True, total_steps
