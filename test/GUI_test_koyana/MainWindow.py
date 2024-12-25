from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget,
                               QFrame, QStackedWidget)
from view1 import View1
from view2 import View2
from view3 import View3
import until.stylecache as stylecache

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 主題切換示例")

        # 創建主窗口佈局
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        # 創建切換視圖按鈕
        self.view_buttons = []
        for i, text in enumerate(["視圖1", "視圖2", "視圖3"]):
            button = QPushButton(text)
            button.setObjectName("viewButton")  # 為按鈕設置統一名稱
            button.setCheckable(True)
            if i == 0:  # 預設選中第一個按鈕
                button.setChecked(True)
            button.clicked.connect(lambda checked, idx=i: self.switch_view(idx))
            self.view_buttons.append(button)

        # 按鈕佈局
        self.button_layout = QHBoxLayout()  # 將按鈕佈局設置為屬性
        for button in self.view_buttons:
            self.button_layout.addWidget(button)
        self.button_layout.setSpacing(0)  # 按鈕之間無間隙
        self.button_layout.setContentsMargins(0, 0, 0, 0)


        # 添加一條分隔線
        separator = QFrame()
        separator.setFixedHeight(1)  # 固定高度，確保分隔線與按鈕貼齊
        separator.setStyleSheet("background-color: #d0d0d0; border: none;")  # 可動態更新主題

        # 添加到主佈局
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(separator)
     

        # 初始化按鈕樣式
        #self.update_button_styles()

        # 創建多視圖
        self.stack = QStackedWidget()
        self.view1 = View1()
        self.view2 = View2()
        self.view3 = View3()
        self.stack.addWidget(self.view1)
        self.stack.addWidget(self.view2)
        self.stack.addWidget(self.view3)

        self.main_layout.addWidget(self.stack)
        
        # 連接信號槽
        self.view3.theme_changed.connect(self.change_theme)

    def switch_view(self, index):
        """切換視圖並更新按鈕狀態"""
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.view_buttons):
            button.setChecked(i == index)
    

    def change_theme(self, theme):
        if theme == "淺色模式":
            self.setStyleSheet(stylecache.apply_light_theme())
        elif theme == "深色模式":
            self.setStyleSheet(stylecache.apply_dark_theme())
