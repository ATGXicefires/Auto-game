from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QLabel, QScrollArea, QPushButton, QSplitter
from PySide6.QtCore import Signal, Qt

class View3(QWidget):
    theme_changed = Signal(str)  # 定義信號

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # 主布局使用 QSplitter 以支持可調整布局
        self.splitter = CustomSplitter(Qt.Horizontal)

        # 左側按鈕區域
        left_widget = QWidget()
        button_layout = QVBoxLayout(left_widget)
        self.buttons = []
        for i in range(5):  # 示例添加5個按鈕
            button = QPushButton(f"定位 {i + 1}")
            button.clicked.connect(lambda _, pos=i: self.scroll_to_position(pos))
            button_layout.addWidget(button)
            self.buttons.append(button)

        button_layout.addStretch()  # 添加彈性空間

        # 右側滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 添加控件到滾動內容中
        self.combo_box = QComboBox()
        self.combo_box.addItems(["淺色模式", "深色模式"])
        self.combo_box.currentIndexChanged.connect(self.emit_theme_change)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)

        scroll_layout.addWidget(QLabel("選擇模式:"))
        scroll_layout.addWidget(self.combo_box)
        scroll_layout.addWidget(QLabel("調整主題:"))
        scroll_layout.addWidget(self.slider)

        # 添加多個滑塊和標籤
        self.additional_sliders = []
        for i in range(10):
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            scroll_layout.addWidget(QLabel(f"額外控件 {i + 1}:"))
            scroll_layout.addWidget(slider)
            self.additional_sliders.append(slider)

        scroll_area.setWidget(scroll_content)

        # 將左側和右側區域添加到 QSplitter
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(scroll_area)

        # 設置預設比例為 1:2
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        # 設置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

    def emit_theme_change(self):
        selected_theme = self.combo_box.currentText()
        self.theme_changed.emit(selected_theme)

    def scroll_to_position(self, position):
        """定位到指定位置"""
        if position < len(self.additional_sliders):
            slider = self.additional_sliders[position]
            slider_parent = slider.parentWidget()
            while slider_parent and not isinstance(slider_parent, QScrollArea):
                slider_parent = slider_parent.parentWidget()
            if slider_parent:
                slider_parent.ensureWidgetVisible(slider)

class CustomSplitter(QSplitter):
    def __init__(self, orientation):
        super().__init__(orientation)

    def mouseDoubleClickEvent(self, event):
        """处理双击事件，仅在分隔条上双击时重置比例为 1:2"""
        for i in range(self.count() - 1):  # 遍历所有分隔条
            handle = self.handle(i)
            if handle.geometry().contains(event.pos()):  # 检查鼠标是否在分隔条上
                # 判断鼠标是否为调整大小样式
                if self.cursor().shape() in (Qt.SplitHCursor, Qt.SplitVCursor):
                    self.setSizes([self.width() // 3, 2 * self.width() // 3])
                    return
        super().mouseDoubleClickEvent(event)