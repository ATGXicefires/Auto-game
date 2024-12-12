from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QCheckBox, QPushButton
from datetime import datetime

class View1(QWidget):
    def __init__(self):
        super().__init__()

        # 主佈局
        layout = QHBoxLayout(self)

        # 左側：包含 3 個 Checkbox 和 1 個按鈕
        left_layout = QVBoxLayout()
        self.checkbox1 = QCheckBox("選項 1")
        self.checkbox2 = QCheckBox("選項 2")
        self.checkbox3 = QCheckBox("選項 3")
        self.button = QPushButton("執行")
        self.button.clicked.connect(self.on_execute_clicked)  # 連接按鈕點擊信號到槽函數
        left_layout.addWidget(self.checkbox1)
        left_layout.addWidget(self.checkbox2)
        left_layout.addWidget(self.checkbox3)
        left_layout.addWidget(self.button)

        # 右側：唯讀文本框顯示日誌
        self.log_textbox = QTextEdit()
        self.log_textbox.setReadOnly(True)  # 設置為唯讀模式
        self.log_textbox.setPlaceholderText("這裡顯示日誌...")  # 添加提示文字
        self.log_textbox.setStyleSheet("border: 1px solid gray; border-radius: 5px;")

        # 將左側和右側加入主佈局
        layout.addLayout(left_layout)
        layout.addWidget(self.log_textbox)

    def append_log(self, message):
        """添加日誌消息到文本框，帶有時間戳"""
        current_time = datetime.now().strftime("%H:%M:%S")  # 獲取當前時間，格式為 hh:mm:ss
        log_entry = f"[{current_time}] {message}"  # 將時間戳添加到消息前
        self.log_textbox.append(log_entry)  # 添加到文本框

    def on_execute_clicked(self):
        """執行按鈕點擊時的行為"""
        self.append_log("正在執行")
