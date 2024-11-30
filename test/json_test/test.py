import main_ui
import sys
import os
import json
import time
import cv2
import pyautogui
    
def wait_10_until_image(image_path, confidence=0.9, timeout=10):
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
        result = pyautogui.locateOnScreen(template, confidence=confidence)
        if result is not None:
            return result
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
    # 導入 sv.json 的變數
    json_variables = load_json_variables('test\json_test\sv.json')
    
    # 使用導入的變數
    print(json_variables)

    def handle_start_button_click(self):
        print("Start Btn have been clicked")
    
    main_ui.main()
    