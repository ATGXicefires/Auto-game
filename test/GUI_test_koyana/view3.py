from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QSlider, QLabel, QScrollArea
from PySide6.QtCore import Signal, Qt

class View3(QWidget):
    theme_changed = Signal(str)  # 定義信號

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # 創建滾動區域和內容Widget
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

        # 示例：多個控件模擬更多空間
        scroll_layout.addWidget(QLabel("選擇模式:"))
        scroll_layout.addWidget(self.combo_box)
        scroll_layout.addWidget(QLabel("調整主題:"))
        scroll_layout.addWidget(self.slider)

        # 添加多個滑塊、標籤示例
        for i in range(10):  
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            scroll_layout.addWidget(QLabel(f"額外控件 {i + 1}:"))
            scroll_layout.addWidget(slider)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def emit_theme_change(self):
        selected_theme = self.combo_box.currentText()
        self.theme_changed.emit(selected_theme)
