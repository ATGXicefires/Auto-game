from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QSlider, QLineEdit, QGraphicsView, QGraphicsScene, QInputDialog
from PySide6.QtGui import QFont, QPixmap, QPainter, QIntValidator
from PySide6.QtCore import Qt, Signal, QThread
from ui_logic import (
    handle_file_selection, 
    clear_json_file, 
    clear_save_data, 
    process_set_button_click, 
    on_zoom_slider_change, 
    show_context_menu, 
    delete_selected_image, 
    update_json_with_input, 
    display_image, 
    clear_detect, 
    clear_adb_settings
)
from functions import (
    get_resource_path, 
    load_json_variables,
    get_max_step_value,
    set_adb_connection,
    load_steps_from_json
)
from log_view import LogView
from process_view import ProcessView
from clicking_functions import Click_step_by_step, ADB_Click_step_by_step
import os
import json

class ClickWorker(QThread):
    finished = Signal()
    log_signal = Signal(str)
    
    def __init__(self, step_array, log_view, is_adb_mode):
        super().__init__()
        self.step_array = step_array
        self.log_view = log_view
        self.is_adb_mode = is_adb_mode

    def run(self):
        # 根據模式選擇不同的點擊函數
        if self.is_adb_mode:
            ADB_Click_step_by_step(self.step_array, self.log_view)
        else:
            Click_step_by_step(self.step_array, self.log_view)
        self.finished.emit()

class ClickWorker2(QThread):
    finished = Signal(bool, int)  # 修改信號，傳送成功狀態和當前步驟
    
    def __init__(self, step_array, log_view, is_adb_mode):
        super().__init__()
        self.step_array = step_array
        self.log_view = log_view
        self.is_adb_mode = is_adb_mode
        
    def run(self):
        if self.is_adb_mode:
            success, current_step = ADB_Click_step_by_step(self.step_array, self.log_view)
        else:
            success, current_step = Click_step_by_step(self.step_array, self.log_view)
        
        self.finished.emit(success, current_step)

class MainWindow(QMainWindow):
    start_signal = Signal()  # 確保信號正確定義

    def on_task_finished(self):
        self.log_view.append_log("任務完成")

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("圖像識別自動化執行工具")
        self.setGeometry(100, 100, 800, 600)

        # 初始化 step_array 和 is_adb_mode
        self.step_array = []  # 初始化為空列表
        self.is_adb_mode = False  # 初始化為 False

        # 創建 QTabWidget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # 設置頁籤的樣式
        self.tabs.setStyleSheet(
            """
            QTabBar::tab {
                height: 40px;  /* 設置頁籤高度 */
                font-size: 16px;  /* 設置字體大小 */
                padding: 10px;  /* 設置內邊距 */
                min-width: 100px;  /* 設置頁籤最小寬度 */
                max-width: 100px;  /* 設置頁籤最大寬度 */
            }
            """
        )

        # 創建主視圖和日誌視圖
        self.main_widget = QWidget()
        self.log_view = LogView(self)
        self.process_view = ProcessView(self)

        # 添加主視圖和日誌視圖到頁籤
        self.tabs.addTab(self.main_widget, "主視圖")
        self.tabs.addTab(self.log_view, "日誌視圖")
        self.tabs.addTab(self.process_view, "流程視圖")

        # 設置主視圖的佈局
        self.setup_main_view()

        self.current_image_key = None  # 用於存儲當前顯示圖片的鍵

        self.load_mode_setting()

    def setup_main_view(self):
        # 主窗口的中心小部件
        main_layout = QHBoxLayout(self.main_widget)
        
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

        # 添加 "清理圖片" 按鈕
        clear_detect_button = QPushButton("清理圖片", self)
        clear_detect_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        clear_detect_button.setFixedHeight(50)  # 設置按鈕高度
        clear_detect_button.setFont(QFont("Arial", 14))  # 設置字體大小
        clear_detect_button.clicked.connect(self.clear_detect)
        left_layout.addWidget(clear_detect_button)

        # 添加 "清除 ADB 設定" 按鈕
        clear_adb_button = QPushButton("清除 ADB 設定", self)
        clear_adb_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        clear_adb_button.setFixedHeight(50)  # 設置按鈕高度
        clear_adb_button.setFont(QFont("Arial", 14))  # 設置字體大小
        clear_adb_button.clicked.connect(lambda: clear_adb_settings(self))
        left_layout.addWidget(clear_adb_button)

        # 添加 "清理存檔" 按鈕
        clear_steps_button = QPushButton("清理存檔", self)
        clear_steps_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        clear_steps_button.setFixedHeight(50)  # 設置按鈕高度
        clear_steps_button.setFont(QFont("Arial", 14))  # 設置字體大小
        clear_steps_button.clicked.connect(lambda: clear_save_data(self))
        left_layout.addWidget(clear_steps_button)

        # 添加 "流程編輯" 按鈕
        preview_button = QPushButton("流程編輯", self)
        preview_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        preview_button.setFixedHeight(50)  # 設置按鈕高度
        preview_button.setFont(QFont("Arial", 14))  # 設置字體大小
        preview_button.clicked.connect(self.process_set_button_click)
        left_layout.addWidget(preview_button)

        # 添加模式選擇開關
        self.mode_button = QPushButton("模式: Windows", self)
        self.mode_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        self.mode_button.setFixedHeight(50)  # 設置按鈕高度
        self.mode_button.setFont(QFont("Arial", 14))  # 設置字體大小
        self.mode_button.setCheckable(True)  # 設置按鈕為可切換狀態
        self.mode_button.clicked.connect(self.toggle_mode)
        left_layout.addWidget(self.mode_button)

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
        self.zoom_slider = QSlider(Qt.Horizontal, self)
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

    def on_button_click(self):
        handle_file_selection(self)

    def clear_detect(self):
        clear_detect(self)

    def clear_save_data(self):
        clear_save_data(self)

    def process_set_button_click(self):
        process_set_button_click(self)

    def on_zoom_slider_change(self):
        on_zoom_slider_change(self)

    def show_context_menu(self, position):
        show_context_menu(self, position)

    def delete_selected_image(self):
        delete_selected_image(self)

    def update_json_with_input(self):
        update_json_with_input(self)

    def toggle_mode(self):
        if self.mode_button.isChecked():
            self.mode_button.setText("模式: ADB")
            # 當切換到 ADB 模式時，自動調用 set_adb_connection
            set_adb_connection(self.log_view, self)
        else:
            self.mode_button.setText("模式: Windows")
        
        # 保存當前模式到 setting.json
        self.save_mode_setting()

    def handle_click_finished(self, success, current_step):
        """處理點擊操作完成的回調"""
        if success:
            self.log_view.append_log(f"所有步驟執行完成！總共執行了 {current_step} 步")
        else:
            self.log_view.append_log(f"執行失敗，在第 {current_step} 步停止")

    def on_start_button_click(self):
        # 這裡是 Start_ON 的邏輯
        # 獲取當前模式
        self.is_adb_mode = self.mode_button.isChecked()
        mode_text = "ADB" if self.is_adb_mode else "Windows"
        self.log_view.append_log(f"當前模式: {mode_text}")

        # 找出 SaveData 資料夾中所有的 json 檔案
        save_path = get_resource_path('SaveData')
        json_files = [f for f in os.listdir(save_path) if f.endswith('.json')]
        
        if not json_files:
            self.log_view.append_log("錯誤：找不到任何存檔檔案")
            return
        
        # 讓使用者選擇要執行的存檔
        item, ok = QInputDialog.getItem(
            self,
            "選擇存檔",
            "請選擇要執行的存檔：",
            json_files,
            0,
            False
        )
        
        if not ok:
            self.log_view.append_log("已取消執行")
            return

        # 根據選擇的檔案執行相應的邏輯
        if item == 'sv.json':
            # 使用原本的邏輯執行 sv.json
            json_path = os.path.join(save_path, item)
            self.log_view.append_log(f"選擇執行存檔: {item}")
            
            json_variables = load_json_variables(json_path)
            max_step_value = 0
            self.log_view.append_log("Start")

            max_step_value = get_max_step_value(json_variables)
            self.log_view.append_log(f"最大 Step[Y] 值: {max_step_value}")

            self.step_array = []
            for i in range(1, max_step_value + 1):
                step_key = f"Step[{i}]"
                if step_key in json_variables:
                    self.step_array.append(json_variables[step_key])
            
            for index in range(max_step_value):
                self.log_view.append_log(f"step_array[{index}]: {self.step_array[index]}")

            self.worker = ClickWorker(self.step_array, self.log_view, self.is_adb_mode)
            self.worker.finished.connect(lambda: self.log_view.append_log("點擊操作完成"))
            self.worker.start()
        
        else:
            # 執行新格式的存檔
            self.step_array, max_step_value = load_steps_from_json(os.path.join(save_path, item))
            self.log_view.append_log(f"載入了 {max_step_value} 個步驟")
            
            self.worker = ClickWorker2(self.step_array, self.log_view, self.is_adb_mode)
            self.worker.finished.connect(self.handle_click_finished)
            self.worker.start()

    def display_image(self, item):
        display_image(self, item)

    def clear_json_file(self):
        clear_json_file(self)  # 確保傳遞 self 以便使用 get_resource_path

    def load_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        if os.path.exists(setting_path):
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                mode = settings.get('detect_mode', 'Windows')
                self.mode_button.setChecked(mode == 'ADB')
                self.mode_button.setText(f"模式: {mode}")

                # 如果模式是 ADB，則調用 set_adb_connection
                if mode == 'ADB':
                    set_adb_connection(self.log_view, self)
        else:
            # 如果文件不存在，默認設置為 Windows 模式
            self.mode_button.setChecked(False)
            self.mode_button.setText("模式: Windows")

    def save_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        try:
            # 先讀取現有的設定
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 只更新 detect_mode，保留其他設定
            settings['detect_mode'] = "ADB" if self.mode_button.isChecked() else "Windows"
            
            # 保存更新後的設定
            with open(setting_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            self.log_view.append_log(f"模式已保存: {settings['detect_mode']}")
            
        except Exception as e:
            self.log_view.append_log(f"保存模式設定時發生錯誤: {str(e)}")

    def toggle_view(self):
        """切換主視圖和日誌視圖"""
        if self.centralWidget() == self.log_view:
            self.setCentralWidget(self.main_widget)  # 切換回主視圖
        else:
            self.setCentralWidget(self.log_view)  # 切換到日誌視圖

    # 其他方法的實現