from PySide6.QtWidgets import QMainWindow, QPushButton, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLineEdit, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QFont, QPixmap, QPainter, QIntValidator
from PySide6.QtCore import Qt, Signal
from ui_logic import handle_file_selection, clear_json_file, clear_cache, clear_steps, on_preview_button_click, display_sorted_images, on_zoom_slider_change, show_context_menu, delete_selected_image, update_json_with_input, toggle_mode, display_image
from functions import get_resource_path, load_json_variables, get_max_step_value, Click_step_by_step

class MainWindow(QMainWindow):
    start_signal = Signal()  # 確保信號正確定義

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("圖像識別自動化執行工具")
        self.setGeometry(100, 100, 800, 600)

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

        # 添加 "清理緩存" 按鈕
        clear_cache_button = QPushButton("清理緩存", self)
        clear_cache_button.setFixedWidth(fixed_width)  # 設置按鈕寬度
        clear_cache_button.setFixedHeight(50)  # 設置按鈕高度
        clear_cache_button.setFont(QFont("Arial", 14))  # 設置字體大小
        clear_cache_button.clicked.connect(self.clear_cache)
        left_layout.addWidget(clear_cache_button)

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
        self.zoom_slider.setRange(10, 200)  # 設定縮放範��為10%到200%
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
        input_layout.setSpacing(0)  # 設置間��為0，讓輸入框緊貼在標籤後面
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

    def on_button_click(self):
        handle_file_selection(self)

    def clear_cache(self):
        clear_cache(self)

    def clear_steps(self):
        clear_steps(self)

    def on_preview_button_click(self):
        on_preview_button_click(self)

    def display_sorted_images(self):
        display_sorted_images(self)

    def on_zoom_slider_change(self):
        on_zoom_slider_change(self)

    def show_context_menu(self, position):
        show_context_menu(self, position)

    def delete_selected_image(self):
        delete_selected_image(self)

    def update_json_with_input(self):
        update_json_with_input(self)

    def toggle_mode(self):
        toggle_mode(self)

    def on_start_button_click(self):
        # 這裡是 Start_ON 的邏輯
        # 獲取當前模式
        is_adb_mode = self.mode_button.isChecked()
        mode_text = "ADB" if is_adb_mode else "Windows"
        print(f"當前模式: {mode_text}")

        # 使用 get_resource_path 來獲取 sv.json 的正確路徑
        json_path = get_resource_path('test/json_test/sv.json')
        # 導入 sv.json 的變數
        json_variables = load_json_variables(json_path)
        max_step_value = 0
        print("Start")
        
        # 最小化主窗口
        self.showMinimized()
        
        # 找出 "Step[Y]" 的最大 Y 值
        max_step_value = get_max_step_value(json_variables)
        print(f"最大 Step[Y] 值: {max_step_value}")

        # 將 Step[Y] 的內容值存入 step_array
        step_array = []
        for i in range(1, max_step_value + 1):
            step_key = f"Step[{i}]"
            if step_key in json_variables:
                step_array.append(json_variables[step_key])
        
        # 打印出 step_array 中的所有值
        for index in range(max_step_value):
            print(f"step_array[{index}]: {step_array[index]}")

        # 根據模式選擇不同的點擊函數
        if is_adb_mode:
            # TODO: 實現 ADB 模式的點擊函數
            print("ADB 模式尚未實現")
        else:
            # 使用原有的 Windows 模式點擊函數
            Click_step_by_step(step_array)

    def display_image(self, item):
        display_image(self, item)

    # 其他方法的實現