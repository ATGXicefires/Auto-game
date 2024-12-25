from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import Qt
from datetime import datetime

class LogView(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #F5F5F5; color: #333333;")

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.append(f"{timestamp} {message}")
