import main_ui
import sys
import os
import json
import time
import cv2
import pyautogui
import threading
from PySide6.QtWidgets import QApplication
    
def wait_until_image(image_path, confidence=0.9, timeout=10):
    '''
    在指定的超時時間內，檢查螢幕上是否出現與給定影像檔案相匹配的影像。
    
    參數:
    image_path: 影像檔案的路徑
    confidence: 匹配的信心度,預設為0.9
    timeout: 超時時間,預設為10秒
    
    返回:
    如果找到匹配的影像，返回其位置；否則返回 None
    '''
    start_time = time.time()
    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    while time.time() - start_time < timeout:
        # 嘗試在螢幕上定位影像
        result = pyautogui.locateOnScreen(template, confidence=confidence, grayscale=True)
        # 如果找到匹配的影像，返回其位置
        if result is not None:
            print(f"匹配成功，位置：{result}")
            return result
        # 打印當前匹配的準確值
        print(f"當前匹配準確值：{confidence}")
        # 每秒檢測一次
        time.sleep(1)
    print("未找到匹配的影像")
    return None

def load_json_variables(file_path):
    '''
    從指定的 JSON 檔案中讀取變數並返回為字典。
    
    參數:
    file_path: JSON 檔案的路徑
    
    返回:
    包含 JSON 內容的字典
    '''
    with open(file_path, 'r', encoding='utf-8') as file:
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
            y_value = int(key.split('[')[1].split(']')[0])
            if y_value > max_step:
                max_step = y_value
    return max_step

# 連接信號到槽函數
def Start_ON():
    max_step_value = 0
    print("Start")
    # 找出 "Step[Y]" 的最大 Y 值
    max_step_value = get_max_step_value(json_variables)
    print(f"最大 Step[Y] 值: {max_step_value}")

    # 將 Step[Y] 的內容值存入 Step[] 陣列
    step_array = []
    for i in range(1, max_step_value + 1):
        step_key = f"Image[{i}]"
        if step_key in json_variables:
            step_array.append(json_variables[step_key])
    
    print(f"Image[] 陣列內容: {step_array}")

if __name__ == "__main__":
    # 創建 QApplication 實例
    app = QApplication(sys.argv)

    # 導入 sv.json 的變數
    json_variables = load_json_variables('test\\json_test\\sv.json')
    # 使用導入的變數
    print(json_variables)
    
    # 創建 MainWindow 的實例
    main_window = main_ui.MainWindow()

    # 連接信號到槽函數
    main_window.start_signal.connect(Start_ON)

    # 顯示主窗口
    main_window.show()

    # 在主執行緒中運行應用程式
    sys.exit(app.exec())
