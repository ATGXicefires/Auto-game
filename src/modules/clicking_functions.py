import cv2
import numpy as np
import pyautogui
import time
from PIL import Image
import os
import subprocess
import json
from functions import get_resource_path
import mss

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
            
            # 構建步驟信息，直接從 JSON 中提取，並提供預設值
            step_info = {
                'location': step_data['location'],
                'timeout': step_data.get('timeout', 30),
                'repeat_clicks': step_data.get('repeat_clicks', 1),  
                'click_interval': step_data.get('click_interval', 1.0)  
            }
            
            print(f"Loaded Step{i}: {step_info}")  # 調試輸出
            
            steps_array.append(step_info)
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
        # 確保 cache 資料夾存在
        cache_dir = get_resource_path('cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # 固定使用 screenshot.png 作為檔案名稱
        cache_file = os.path.join(cache_dir, 'screenshot.png')
        
        # 使用 ADB 截圖並保存到手機
        subprocess.run('adb shell screencap -p /sdcard/screenshot.png', shell=True, check=True)
        # 將截圖從手機拉到電腦的 cache 資料夾
        subprocess.run(f'adb pull /sdcard/screenshot.png "{cache_file}"', shell=True, check=True)
        # 刪除手機上的截圖
        subprocess.run('adb shell rm /sdcard/screenshot.png', shell=True, check=True)
        
        # 讀取截圖
        screenshot = cv2.imread(cache_file)
        
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

def detect_and_click_image(template_path, log_view, confidence=0.9, timeout=30, is_adb_mode=False, max_retries=3, repeat_clicks=1, click_interval=1):
    """
    在螢幕上偵測圖片並點擊
    
    Args:
        template_path (str): 模板圖片路徑
        log_view: 日誌視圖實例
        confidence (float): 匹配信心值
        timeout (int): 超時時間(秒)
        is_adb_mode (bool): 是否使用 ADB 模式
        max_retries (int): 最大重試次數
        repeat_clicks (int): 重複點擊次數
        click_interval (float): 點擊間隔時間(秒)
    
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

    def take_screenshot():
        retry_count = 0
        while retry_count < max_retries:
            try:
                if is_adb_mode:
                    screenshot = ADB_screenshot()
                    if screenshot is None:
                        raise Exception("ADB 截圖失敗")
                else:
                    with mss.mss() as sct:
                        monitor = sct.monitors[0]  # 0 表示所有螢幕
                        screenshot = sct.grab(monitor)
                        screenshot = np.array(screenshot)
                        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                return screenshot
            except Exception as e:
                retry_count += 1
                log_view.append_log(f"截圖失敗 (嘗試 {retry_count}/{max_retries}): {str(e)}")
                time.sleep(1)
        return None
        
    def perform_clicks(x, y, repeat_clicks, click_interval, is_adb_mode, log_view):
        """執行點擊操作，支援重複點擊"""
        log_view.append_log(f"開始執行點擊，總次數: {repeat_clicks}, 間隔: {click_interval}秒")
        for click_count in range(repeat_clicks):
            try:
                if is_adb_mode:
                    if not ADB_click(x, y):
                        log_view.append_log(f"ADB 點擊失敗")
                        return False
                else:
                    pyautogui.moveTo(x, y, duration=0.5)
                    pyautogui.click()
                
                log_view.append_log(f"完成第 {click_count + 1}/{repeat_clicks} 次點擊")
                
                if click_count < repeat_clicks - 1:  # 如果不是最後一次點擊
                    log_view.append_log(f"等待 {click_interval} 秒後進行下一次點擊")
                    time.sleep(click_interval)
                    
            except Exception as e:
                log_view.append_log(f"第 {click_count + 1} 次點擊失敗: {str(e)}")
                return False
        return True

    start_time = time.time()
    log_view.append_log(f"開始尋找圖片，超時時間設定為 {timeout} 秒")
    template = read_image_with_pil(template_path)
    
    if template is None:
        log_view.append_log("無法讀取模板圖片")
        return None

    while time.time() - start_time < timeout:
        try:
            screenshot = take_screenshot()
            if screenshot is None:
                log_view.append_log("無法取得螢幕截圖")
                continue

            # 執行模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                template_height, template_width = template.shape[:2]
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                log_view.append_log(f"找到匹配位置: {max_loc}, 匹配值: {max_val}, 中心點: ({center_x}, {center_y})")

                if perform_clicks(center_x, center_y, repeat_clicks, click_interval, is_adb_mode, log_view):
                    log_view.append_log(f"完成所有點擊操作 (共 {repeat_clicks} 次)")
                    return (center_x, center_y)
                else:
                    log_view.append_log("點擊操作失敗")
                    return None

            remaining_time = int(timeout - (time.time() - start_time))
            if remaining_time > 0:
                log_view.append_log(f"當前匹配準確值：{max_val}，剩餘時間：{remaining_time}秒")
            time.sleep(0.5)

        except Exception as e:
            log_view.append_log(f"處理過程發生錯誤: {str(e)}")
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
        timeout = step.get('timeout', 30)  # 提供預設值
        repeat_clicks = step.get('repeat_clicks', 1)  # 提供預設值
        click_interval = step.get('click_interval', 1.0)  # 提供預設值
        
        log_view.append_log(
            f"正在執行第 {current_step}/{total_steps} 步: {step['location']}\n"
            f"超時設定: {timeout}秒, 點擊次數: {repeat_clicks}, 間隔: {click_interval}秒"
        )
        
        result = detect_and_click_image(
            template_path=template_path,
            log_view=log_view,
            timeout=timeout,
            is_adb_mode=False,
            repeat_clicks=repeat_clicks,  # 傳遞 repeat_clicks
            click_interval=click_interval  # 傳遞 click_interval
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
        repeat_clicks = step['repeat_clicks']  # 獲取重複點擊次數
        click_interval = step['click_interval']  # 獲取點擊間隔
        
        log_view.append_log(
            f"正在執行第 {current_step}/{total_steps} 步: {step['location']}\n"
            f"超時設定: {timeout}秒, 點擊次數: {repeat_clicks}, 間隔: {click_interval}秒"
        )
        
        result = detect_and_click_image(
            template_path=template_path,
            log_view=log_view,
            timeout=timeout,
            is_adb_mode=True,
            repeat_clicks=repeat_clicks,  # 傳遞重複點擊次數
            click_interval=click_interval  # 傳遞點擊間隔
        )
        
        if result is None:
            log_view.append_log(f"步驟 {current_step} 失敗: 無法找到或點擊 {step['location']}")
            return False, current_step
            
        log_view.append_log(f"步驟 {current_step} 完成")
        time.sleep(1)
    
    return True, total_steps
