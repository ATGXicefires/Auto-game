import sys
import os
import shutil
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Test Window")
        self.setGeometry(100, 100, 800, 600)
        
        # 添加第一個按鈕
        button1 = QPushButton("Btn_1", self)
        button1.setGeometry(100, 100, 200, 50)
        button1.clicked.connect(self.on_button_click)

        # 添加第二個按鈕
        button2 = QPushButton("Btn_2", self)
        button2.setGeometry(100, 200, 200, 50) 
        button2.clicked.connect(self.on_new_button_click)

        # 添加 "Start" 按鈕
        start_button = QPushButton("Start", self)
        start_button.setGeometry(100, 300, 200, 50)
        start_button.clicked.connect(self.on_start_button_click)

    def on_button_click(self):
        self.handle_file_selection("Step_1")

    def on_new_button_click(self):
        self.handle_file_selection("Step_2")

    def handle_file_selection(self, step_key):
        # 打開文件選擇對話框
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        
        if file_path:
            # 確保目標資料夾存在
            target_dir = "test/json_test/cache"
            os.makedirs(target_dir, exist_ok=True)
            
            # 獲取目標路徑
            target_path = os.path.join(target_dir, os.path.basename(file_path))
            
            # 複製文件到目標資料夾
            shutil.copy(file_path, target_path)
            print(f"Image copied to {target_path}")

            # 將目標路徑轉換為相對路徑
            relative_path = os.path.relpath(target_path, start=os.getcwd())

            # 儲存路徑到 JSON 檔案
            json_path = "test/json_test/sv.json"
            self.save_path_to_json(relative_path, json_path, step_key)

    def save_path_to_json(self, file_path, json_path, step_key):
        # 讀取現有的 JSON 資料
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}  # 如果不是字典，重置為空字典
                except json.JSONDecodeError:
                    data = {}  # 如果 JSON 解析失敗，重置為空字典
        else:
            data = {}

        # 添加新的路徑
        data[step_key] = file_path

        # 寫入 JSON 檔案
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Path saved to {json_path}")

    def on_start_button_click(self):
        # 讀取現有的 JSON 資料
        json_path = "test/json_test/sv.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}  # 如果不是字典，重置為空字典
                except json.JSONDecodeError:
                    data = {}  # 如果 JSON 解析失敗，重置為空字典
        else:
            data = {}

        # 添加 "Start": "1" 到 JSON 資料
        data["Start"] = "1"

        # 寫入 JSON 檔案
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f'"Start": "1" added to {json_path}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())