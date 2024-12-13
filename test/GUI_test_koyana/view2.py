from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, 
                               QGraphicsView, QGraphicsScene, QGraphicsRectItem, QFileDialog)
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt

class View2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.file_button = QPushButton("選擇文件")
        self.path_display = QPlainTextEdit()
        self.path_display.setReadOnly(True)
        self.file_button.clicked.connect(self.open_file_dialog)

        left_layout.addWidget(self.file_button)
        left_layout.addWidget(self.path_display)
        layout.addLayout(left_layout)
        self.setLayout(layout)

        # 添加自定義畫布視圖
        self.canvas_view = CanvasView()
        layout.addWidget(self.canvas_view)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇文件")
        if file_path:
            self.path_display.setPlainText(file_path)
class CanvasView(QGraphicsView):
    def __init__(self):
        super().__init__()

        # 创建场景并设置到视图中
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 添加示例图形到场景中
        self.scene.addItem(QGraphicsRectItem(0, 0, 200, 200))  # 添加矩形

        # 配置视图
        self.setRenderHint(QPainter.Antialiasing)  # 设置抗锯齿渲染
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # 启用拖动模式
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)  # 设置缩放中心点

    def wheelEvent(self, event):
        """使用滚轮缩放画布"""
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:  # 滚轮向上滚动
            self.scale(zoom_factor, zoom_factor)
        else:  # 滚轮向下滚动
            self.scale(1 / zoom_factor, 1 / zoom_factor)