from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QWheelEvent, QKeyEvent
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
        
        # 設置初始字體大小
        self.current_font = self.log_text_edit.font()
        self.current_font_size = self.current_font.pointSize()
        
        # 安裝事件過濾器
        self.log_text_edit.installEventFilter(self)
        
        layout.addWidget(self.log_text_edit)
    
    def eventFilter(self, obj, event):
        """事件過濾器，處理滾輪和按鍵事件"""
        if obj == self.log_text_edit:
            # 處理 Ctrl + 滾輪事件
            if event.type() == QWheelEvent.Type:
                if event.modifiers() == Qt.ControlModifier:
                    delta = event.angleDelta().y()
                    if delta > 0:
                        self.zoom_in()
                    else:
                        self.zoom_out()
                    return True
            
            # 處理 Ctrl + +/- 按鍵事件
            elif event.type() == QKeyEvent.Type:
                if event.modifiers() == Qt.ControlModifier:
                    if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                        self.zoom_in()
                        return True
                    elif event.key() == Qt.Key_Minus:
                        self.zoom_out()
                        return True
        
        return super().eventFilter(obj, event)
    
    def zoom_in(self):
        """放大文字"""
        if self.current_font_size < 72:  # 設置最大字體大小限制
            self.current_font_size += 1
            self.update_font_size()
    
    def zoom_out(self):
        """縮小文字"""
        if self.current_font_size > 6:  # 設置最小字體大小限制
            self.current_font_size -= 1
            self.update_font_size()
    
    def update_font_size(self):
        """更新字體大小"""
        self.current_font.setPointSize(self.current_font_size)
        self.log_text_edit.setFont(self.current_font)
        
    def append_log(self, message):
        """添加日誌信息到文本編輯器"""
        current_time = datetime.now().strftime("%H:%M:%S")  # 獲取當前時間，格式為 hh:mm:ss
        self.log_text_edit.append(f"[{current_time}] {message}")
        
        # 將滾動條移動到最底部
        scrollbar = self.log_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())