import main_ui
import sys
import os
import json
import time
import cv2
import pyautogui
import threading
    
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
    
    # 將 "Start" 預設為 0
    data["Start"] = "0" # 到時候可以判斷是否為1來決定是否要執行
    
    # 將更新後的資料寫回 JSON 檔案
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    return data

if __name__ == "__main__":
    Start = False
    # 導入 sv.json 的變數
    json_variables = load_json_variables('test\\json_test\\sv.json')
    # 使用導入的變數
    print(json_variables)
    
    # 在新執行緒中運行 main_ui.main()
    ui_thread = threading.Thread(target=main_ui.main)
    ui_thread.start()

    while ui_thread.is_alive():
        # 重新載入 JSON 檔案以檢查 "Start" 的值
        with open('test\\json_test\\sv.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 檢查 "Start" 是否為 "1"
        if data.get("Start") == "1":
            print("Start")
            Start = True
            break
        # 可以加入一些延遲以避免過於頻繁的檢查
        time.sleep(1)
    
    if not ui_thread.is_alive():
        print("UI 執行緒已結束，終止程式")
        sys.exit()

    if Start:
        print(main_ui.get_max_step_value())

