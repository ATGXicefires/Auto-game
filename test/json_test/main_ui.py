import sys
import os
import shutil
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QMenu, QLineEdit, QMessageBox
from PySide6.QtGui import QPixmap, QIntValidator
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Test Window")
        self.setGeometry(100, 100, 800, 600)
        
        # 清空 JSON 檔案
        self.clear_json_file()

        # 主窗口的中心小部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 水平佈局
        main_layout = QHBoxLayout(central_widget)
        
        # 左側垂直佈局
        left_layout = QVBoxLayout()
        
        # 設置固定寬度
        fixed_width = 200

        # 添加第一個按鈕
        button1 = QPushButton("選擇圖片", self)
        button1.setFixedWidth(fixed_width)  # 設置按鈕寬度
        button1.clicked.connect(self.on_button_click)
        left_layout.addWidget(button1)

        # 添加 "Start" 按鈕
        start_button = QPushButton("程式開始", self)
        start_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        start_button.clicked.connect(self.on_start_button_click)
        left_layout.addWidget(start_button)

        # 添加圖片列表
        self.image_list_widget = QListWidget(self)
        self.image_list_widget.setFixedWidth(fixed_width)  # 設置固定寬度
        self.image_list_widget.itemClicked.connect(self.display_image)
        self.image_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list_widget.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.image_list_widget)

        # 添加滑桿
        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setFixedWidth(fixed_width)  # 設置滑桿寬度
        self.zoom_slider.setRange(10, 200)  # 設定縮放範圍為10%到200%
        self.zoom_slider.setValue(75)  # 預設值為75%
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_change)
        left_layout.addWidget(self.zoom_slider)

        # 將左側佈局添加到主佈局
        main_layout.addLayout(left_layout)

        # 添加圖片顯示區域到右側
        self.image_label = QLabel(self)
        main_layout.addWidget(self.image_label)

        # 在圖片顯示區域上添加一個輸入框
        self.input_box = QLineEdit(self)
        self.input_box.setValidator(QIntValidator(0, 30))  # 限制輸入為0到30的整數
        self.input_box.setFixedSize(50, 50)  # 設置為正方形
        self.input_box.setStyleSheet("background-color: white; color: black;")  # 設置背景顏色為白色，字體顏色為黑色
        self.input_box.move(10, 10)  # 設置位置在左上角
        self.input_box.setAlignment(Qt.AlignCenter)  # 文字居中
        self.input_box.setPlaceholderText("0")  # 預設提示文字
        self.input_box.editingFinished.connect(self.update_json_with_input)  # 當輸入框編輯完成時更新 JSON

        self.current_image_key = None  # 用於存儲當前顯示圖片的鍵

        # 設置滾輪事件
        self.image_label.wheelEvent = self.wheelEvent

    def clear_json_file(self):
        # 清空 JSON 檔案並設置預設值
        json_path = "test/json_test/sv.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({"Start": "0"}, f, ensure_ascii=False, indent=4)
        print(f"Cleared {json_path} with default 'Start': '0'")

    def on_button_click(self):
        self.handle_file_selection()

    def handle_file_selection(self):
        # 打開文件選擇對話框，允許多選
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        
        if file_paths:
            # 確保目標資料夾存在
            target_dir = "test/json_test/cache"
            os.makedirs(target_dir, exist_ok=True)
            
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

            # 找到目前最大的 Img[X] 的 X 值
            max_index = 0
            for key in data.keys():
                if key.startswith("Img["):
                    try:
                        index = int(key[4:-1])
                        if index > max_index:
                            max_index = index
                    except ValueError:
                        continue

            # 複製文件到目標資料夾並更新 JSON
            for i, file_path in enumerate(file_paths, start=1):
                target_path = os.path.join(target_dir, os.path.basename(file_path))
                shutil.copy(file_path, target_path)
                print(f"Image copied to {target_path}")

                # 將目標路徑轉換為相對路徑
                relative_path = os.path.relpath(target_path, start=os.getcwd())

                # 儲存路徑到 JSON 檔案
                data[f"Img[{max_index + i}]"] = relative_path

                # 在列表中添加新圖片的檔名
                self.image_list_widget.addItem(os.path.basename(relative_path))

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Paths saved to {json_path}")

    def display_image(self, item):
        # 顯示選中的圖片
        # 需要從 JSON 中獲取完整路徑
        json_path = "test/json_test/sv.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 找到對應的完整路徑
        for key, path in data.items():
            if os.path.basename(path) == item.text():
                self.current_pixmap = QPixmap(path)
                self.update_image_display()
                self.current_image_key = key  # 記錄當前圖片的鍵
                self.input_box.setText(key.split('[')[-1].split(']')[0])  # 顯示 Img[X] 的 X 值
                break

    def update_image_display(self):
        # 根據滑桿的值縮放圖片
        scale_factor = self.zoom_slider.value() / 100.0
        scaled_pixmap = self.current_pixmap.scaled(self.current_pixmap.size() * scale_factor, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

    def on_zoom_slider_change(self):
        # 當滑桿值改變時更新圖片顯示
        self.update_image_display()

    def wheelEvent(self, event):
        # 使用 Ctrl + 滾輪來縮放圖片
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y() / 120  # 每次滾動的單位
            new_value = self.zoom_slider.value() + delta * 5  # 每次滾動改變5%
            self.zoom_slider.setValue(max(10, min(200, new_value)))  # 限制在10%到200%之間

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

    def closeEvent(self, event):
        # 結束應用程式
        QApplication.quit()

    def show_context_menu(self, position):
        # 創建右鍵菜單
        menu = QMenu()
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.image_list_widget.mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_image()

    def delete_selected_image(self):
        # 刪除選中的圖片
        selected_item = self.image_list_widget.currentItem()
        if selected_item:
            image_name = selected_item.text()
            self.image_list_widget.takeItem(self.image_list_widget.row(selected_item))
            self.remove_image_from_json(image_name)

    def remove_image_from_json(self, image_name):
        # 從 JSON 中刪除圖片
        json_path = "test/json_test/sv.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 找到並刪除對應的圖片路徑
        key_to_remove = None
        for key, path in data.items():
            if os.path.basename(path) == image_name:
                key_to_remove = key
                break

        if key_to_remove:
            del data[key_to_remove]

            # 更新 JSON 文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Deleted {image_name} from JSON")

    def update_json_with_input(self):
        # 更新 JSON 文件中的 Img[X] 值
        if self.current_image_key:
            json_path = "test/json_test/sv.json"
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 更新對應的 Img[X] 值
            new_value = self.input_box.text()
            if new_value.isdigit():
                new_key = f"Img[{new_value}]"
                if new_key in data:
                    QMessageBox.warning(self, "重複的數字", f"數字 {new_value} 已被使用，請選擇其他數字。")
                else:
                    data[new_key] = data.pop(self.current_image_key)
                    self.current_image_key = new_key  # 更新當前圖片的鍵

                    # 寫入更新後的 JSON 文件
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"Updated JSON with new key: {new_key}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())