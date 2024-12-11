import sys
import os
import shutil
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QMenu, QLineEdit, QMessageBox, QGraphicsView, QGraphicsScene, QStyle, QStyleOptionSlider, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QIntValidator, QPainter, QFont, QPen
from PySide6.QtCore import Qt, Signal

class ZoomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
    ''' # 功能沒做出來，到時候再說，先跳過 (非重點功能)
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        handle_rect = self.style().subControlRect(QStyle.CC_Slider, option, QStyle.SC_SliderHandle, self)
        
        # 設置字體和顏色
        painter.setFont(QFont("Arial", 12))
        painter.setPen(Qt.black)
        
        # 在滑桿的圓點上方顯示當前值
        value_text = f"{self.value()}%"
        text_rect = handle_rect.translated(0, -30)  # 將文字位置上移
        
        # 設置背景顏色
        painter.setBrush(Qt.white)
        painter.setPen(Qt.NoPen)  # 不要邊框
        painter.drawRect(text_rect)  # 繪製背景矩形
        
        # 設置字體顏色
        painter.setPen(Qt.black)
        # 使用 drawText 的另一種方式來確保文字顯示
        painter.drawText(text_rect.x(), text_rect.y(), text_rect.width(), text_rect.height(), Qt.AlignCenter, value_text)
    '''

class MainWindow(QMainWindow):
    start_signal = Signal()  # 確保信號正確定義

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("圖像識別自動化執行工具")
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

        # 添加選擇圖片按鈕
        button1 = QPushButton("選擇圖片", self)
        button1.setFixedWidth(fixed_width)  # 設置按鈕寬度
        button1.setFixedHeight(50)  # 設置按鈕高度
        button1.setFont(QFont("Arial", 14))  # 設置字體大小
        button1.clicked.connect(self.on_button_click)
        left_layout.addWidget(button1)

        # 添加 "清除步驟" 按鈕
        clear_steps_button = QPushButton("清除已設置步驟", self)
        clear_steps_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        clear_steps_button.setFixedHeight(50)  # 設置按鈕高度
        clear_steps_button.setFont(QFont("Arial", 14))  # 設置字體大小
        clear_steps_button.clicked.connect(self.clear_steps)
        left_layout.addWidget(clear_steps_button)

        # 添加 "流程預覽" 按鈕
        preview_button = QPushButton("流程預覽", self)
        preview_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        preview_button.setFixedHeight(50)  # 設置按鈕高度
        preview_button.setFont(QFont("Arial", 14))  # 設置字體大小
        preview_button.clicked.connect(self.on_preview_button_click)
        left_layout.addWidget(preview_button)

        # 添加 "Start" 按鈕
        start_button = QPushButton("程式開始", self)
        start_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        start_button.setFixedHeight(50)  # 設置按鈕高度
        start_button.setFont(QFont("Arial", 14))  # 設置字體大小
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
        self.zoom_slider = ZoomSlider(Qt.Horizontal, self)
        self.zoom_slider.setFixedWidth(fixed_width)  # 設置滑桿寬度
        self.zoom_slider.setRange(10, 200)  # 設定縮放範圍為10%到200%
        self.zoom_slider.setValue(75)  # 預設值為75%
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_change)
        left_layout.addWidget(self.zoom_slider)

        # 將左側佈局添加到主佈局
        main_layout.addLayout(left_layout)

        # 創建一個垂直佈局來包含圖片顯示區和輸入框
        right_layout = QVBoxLayout()

        # 在圖片顯示區域上方添加一個標籤和輸入框
        label = QLabel("設定執行順序:", self)  # 添加標籤
        label.setFont(QFont("Arial", 14))  # 設置字體大小與按鈕相同

        self.input_box = QLineEdit(self)
        self.input_box.setValidator(QIntValidator(1, 50))  # 限制輸入為1到50的整數
        self.input_box.setFixedSize(50, 50)  # 設置為正方形
        self.input_box.setStyleSheet("background-color: white; color: black;")  # 設置背景顏色為白色，字體顏色為黑色
        self.input_box.setAlignment(Qt.AlignCenter)  # 文字居中
        self.input_box.setPlaceholderText("0")  # 預設提示文字
        self.input_box.editingFinished.connect(self.update_json_with_input)  # 當輸入框編輯完成時更新 JSON

        # 創建一個水平佈局來包含標籤和輸入框
        input_layout = QHBoxLayout()
        input_layout.setSpacing(0)  # 設置間距為0，讓輸入框緊貼在標籤後面
        input_layout.addWidget(label, alignment=Qt.AlignLeft)  # 添加標籤到水平佈局並靠左對齊
        input_layout.addWidget(self.input_box, alignment=Qt.AlignLeft)  # 添加輸入框到水平佈局並靠左對齊

        # 將水平佈局添加到右側佈局
        right_layout.addLayout(input_layout)
        right_layout.setAlignment(input_layout, Qt.AlignTop | Qt.AlignLeft)  # 設置對齊方式

        # 使用 QGraphicsView 和 QGraphicsScene 來顯示圖片
        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 啟用拖曳模式
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setFixedSize(1280, 720)  # 固定圖片顯示區域的尺寸
        self.graphics_view.setStyleSheet("border: 5px solid white;")  # 設置白色邊框
        right_layout.addWidget(self.graphics_view)

        # 將右側佈局添加到主佈局
        main_layout.addLayout(right_layout)

        self.current_image_key = None  # 用於存儲當前顯示圖片的鍵

        self.display_sorted_images()  # 在初始化時顯示排序後的圖片

    def clear_json_file(self):
        # 清空 JSON 檔案並設置為全空
        json_path = self.get_resource_path("test/json_test/sv.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)  # 設置為空字典
        print(f"Cleared {json_path} and set to empty")

    def get_resource_path(self, relative_path):
        """獲取資源文件的正確路徑"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def on_button_click(self):
        self.handle_file_selection()

    def handle_file_selection(self):
        # 打開文件選擇對話框，允許多選
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        
        if file_paths:
            target_dir = self.get_resource_path("test/json_test/cache")
            os.makedirs(target_dir, exist_ok=True)
            
            json_path = self.get_resource_path("test/json_test/sv.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, dict):
                            data = {}
                    except json.JSONDecodeError:
                        data = {}
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
        json_path = self.get_resource_path("test/json_test/sv.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 找到對應的完整路徑
        for key, path in data.items():
            if os.path.basename(path) == item.text():
                pixmap = QPixmap(path)
                self.graphics_scene.clear()  # 清除現有的場景
                pixmap_item = self.graphics_scene.addPixmap(pixmap)  # 添加新的圖片
                pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsMovable)  # 設置圖片為可移動
                self.current_image_key = key  # 記錄當前圖片的鍵
                # self.input_box.setText(key.split('[')[-1].split(']')[0])  # 不顯示 Img[X] 的 X 值
                self.input_box.setText("")  # 設置為空，不顯示任何內容
                
                # 新增以下代碼以將圖片置中並設置縮放
                self.graphics_view.setSceneRect(pixmap.rect())  # 設置場景矩形
                self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)  # 置中圖片
                self.graphics_view.scale(0.75, 0.75)  # 設置縮放為 75%
                
                break

    def on_zoom_slider_change(self):
        # 當滑桿值改變時更新圖片顯示
        scale_factor = self.zoom_slider.value() / 100.0
        self.graphics_view.resetTransform()  # 重置任何現有的變換
        self.graphics_view.scale(scale_factor, scale_factor)  # 根據滑桿的值縮放圖片
        self.zoom_slider.setToolTip(f"{self.zoom_slider.value()}%")  # 更新滑桿的提示文字

    def wheelEvent(self, event):
        # 使用 Ctrl + 滾輪來縮放圖片
        if event.modifiers() == Qt.ControlModifier:
            # 獲取鼠標在視圖中的位置
            mouse_pos = self.graphics_view.mapToScene(event.position().toPoint())
            # 檢查鼠標下的項目
            item = self.graphics_scene.itemAt(mouse_pos, self.graphics_view.transform())
            if isinstance(item, QGraphicsPixmapItem):
                # 計算縮放因子
                delta = event.angleDelta().y() / 120  # 每次滾動的單位
                scale_factor = 1 + delta * 0.1  # 每次滾動改變10%
                # 縮放圖片
                item.setScale(item.scale() * scale_factor)

    def on_start_button_click(self):
        print("Start button clicked")  # 添加打印語句以確認按鈕被點擊
        self.start_signal.emit()  # 發出信號
        print("Signal emitted")  # 確認信號已發出

    def closeEvent(self, event):
        # 結束應用程式
        QApplication.quit()

    def show_context_menu(self, position):
        # 創建右鍵菜單
        menu = QMenu()
        delete_action = menu.addAction("刪除圖片")
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
        json_path = self.get_resource_path("test/json_test/sv.json")
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
        # 更新 JSON 文件中的 Step[Y] 值
        if self.current_image_key:
            json_path = self.get_resource_path("test/json_test/sv.json")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 更新對應的 Step[Y] 值
            new_value = self.input_box.text()
            if new_value.isdigit():
                new_key = f"Step[{new_value}]"
                if new_key in data:
                    QMessageBox.warning(self, "重複的數字", f"數字 {new_value} 已被使用，請選擇其他數字。")
                else:
                    # 保留 Img[X]，同時新增 Step[Y]
                    data[new_key] = data[self.current_image_key]
                    self.current_image_key = new_key  # 更新當前圖片的鍵

                    # 寫入更新後的 JSON 文件
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"Added new key: {new_key} with value from {self.current_image_key}")

    def on_preview_button_click(self):
        # 處理 "流程預覽" 按鈕的點擊事件
        print("流程預覽按鈕被點擊")
        self.display_sorted_images()  # 顯示排序後的圖片

    def display_sorted_images(self):
        # 讀取 JSON 檔案並按 Step[Y] 排序顯示圖片
        json_path = self.get_resource_path("test/json_test/sv.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 過濾出 Step[Y] 鍵並排序
        step_items = {k: v for k, v in data.items() if k.startswith("Step[")}
        sorted_steps = sorted(step_items.items(), key=lambda item: int(item[0][5:-1]))

        # 清除現有的場景
        self.graphics_scene.clear()

        # 設置初始位置
        y_offset = 0
        previous_item = None

        # 依序顯示圖片
        for _, path in sorted_steps:
            pixmap = QPixmap(path)
            
            # 自動縮放圖片以適應顯示區域
            scaled_pixmap = pixmap.scaled(self.graphics_view.width(), self.graphics_view.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            item = self.graphics_scene.addPixmap(scaled_pixmap)
            item.setPos(0, y_offset)  # 設置每張圖片的位置
            item.setFlag(QGraphicsPixmapItem.ItemIsMovable)  # 設置圖片為可移動
            
            # 如果有前一個圖片，則添加箭頭
            if previous_item:
                pen = QPen(Qt.black)  # 使用 QPen 來設置箭頭顏色
                arrow = self.graphics_scene.addLine(previous_item.x() + previous_item.pixmap().width() / 2,
                                                    previous_item.y() + previous_item.pixmap().height(),
                                                    item.x() + item.pixmap().width() / 2,
                                                    item.y(),
                                                    pen)
                arrow.setZValue(-1)  # 確保箭頭在圖片下方
            
            previous_item = item
            y_offset += scaled_pixmap.height() + 10  # 更新 y_offset 以便下一張圖片不重疊

    def clear_steps(self):
        # 清空 JSON 檔案中的 Step[Y] 條目，保留 Img[X] 條目
        json_path = self.get_resource_path("test/json_test/sv.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 刪除所有 Step[Y] 條目
            keys_to_remove = [key for key in data.keys() if key.startswith("Step[")]
            for key in keys_to_remove:
                del data[key]

            # 更新 JSON 文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("所有 Step[Y] 條目已清除")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())