from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from datetime import datetime

class LogView(QWidget):
    def __init__(self, parent=None):
        super(LogView, self).__init__(parent)
        self.setWindowTitle("日誌視圖")
        
        # 創建一個垂直佈局
        layout = QVBoxLayout(self)
        
        # 創建一個文本編輯器來顯示日誌
        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)  # 設置為只讀
        self.log_text_edit.setStyleSheet("color: lightblue; background-color: black;")  # 設置字體顏色為藍色
        layout.addWidget(self.log_text_edit)
        
    def append_log(self, message):
        """添加日誌信息到文本編輯器"""
        current_time = datetime.now().strftime("%H:%M:%S")  # 獲取當前時間，格式為 hh:mm:ss
        self.log_text_edit.append(f"[{current_time}] {message}")