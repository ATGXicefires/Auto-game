from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent, QPen, QColor, QPainter, QMouseEvent
from PySide6.QtCore import Qt, QLineF
import shutil
import os
from functions import get_resource_path

class TestView(QWidget):
    def __init__(self, parent=None):
        super(TestView, self).__init__(parent)
        self.setAcceptDrops(True)  # 啟用拖放功能

        # 設置佈局
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # 創建圖片顯示區域
        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)  # 使用 QPainter 的屬性
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)  # 使用 QPainter 的屬性
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 啟用拖曳模式
        layout.addWidget(self.graphics_view)

        # 添加提示標籤
        self.label = QLabel("拖曳圖片到此區域", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16, QFont.Bold))  # 設置字體大小和粗體
        self.label.setStyleSheet("color: white; background-color: darkblue; padding: 10px;")  # 設置字體顏色和背景顏色
        layout.addWidget(self.label)

        # 用於存儲拉線起點、臨時線條和正式連線
        self.start_dot = None
        self.temp_line = None
        self.lines = []

        # 添加新的實例變數
        self.current_line = None
        self.last_mouse_pos = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                self.handle_image_drop(file_path)

    def handle_image_drop(self, file_path):
        detect_folder = get_resource_path('detect')
        if not os.path.exists(detect_folder):
            os.makedirs(detect_folder)

        file_name = os.path.basename(file_path)
        destination_path = os.path.join(detect_folder, file_name)
        shutil.copy(file_path, destination_path)

        pixmap = QPixmap(destination_path)
        if pixmap.isNull():
            return

        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.graphics_scene.addItem(pixmap_item)

        # 添加小白點
        self.add_white_dots(pixmap_item)

        self.label.setText(f"已載入圖片: {file_name}")

    def add_white_dots(self, pixmap_item):
        """在圖片的上下左右添加小白點"""
        rect_size = 10  # 小白點的大小
        offset = 10  # 小白點與圖片的距離
        pen = QPen(QColor("white"))
        pen.setWidth(0)  # 設置邊框寬度為0

        # 獲取圖片的邊界
        rect = pixmap_item.boundingRect()

        # 上
        top_dot = QGraphicsRectItem(rect.width() / 2 - rect_size / 2, -rect_size / 2 - offset, rect_size, rect_size, pixmap_item)
        top_dot.setPen(pen)
        top_dot.setBrush(QColor("white"))
        top_dot.setData(0, "dot")  # 標記為小白點
        self.graphics_scene.addItem(top_dot)

        # 下
        bottom_dot = QGraphicsRectItem(rect.width() / 2 - rect_size / 2, rect.height() - rect_size / 2 + offset, rect_size, rect_size, pixmap_item)
        bottom_dot.setPen(pen)
        bottom_dot.setBrush(QColor("white"))
        bottom_dot.setData(0, "dot")
        self.graphics_scene.addItem(bottom_dot)

        # 左
        left_dot = QGraphicsRectItem(-rect_size / 2 - offset, rect.height() / 2 - rect_size / 2, rect_size, rect_size, pixmap_item)
        left_dot.setPen(pen)
        left_dot.setBrush(QColor("white"))
        left_dot.setData(0, "dot")
        self.graphics_scene.addItem(left_dot)

        # 右
        right_dot = QGraphicsRectItem(rect.width() - rect_size / 2 + offset, rect.height() / 2 - rect_size / 2, rect_size, rect_size, pixmap_item)
        right_dot.setPen(pen)
        right_dot.setBrush(QColor("white"))
        right_dot.setData(0, "dot")
        self.graphics_scene.addItem(right_dot)

    def mousePressEvent(self, event: QMouseEvent):
        """處理鼠標按下事件"""
        scene_pos = self.graphics_view.mapToScene(event.pos())
        item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
        
        if item and item.data(0) == "dot":
            # 點擊在小白點上，準備開始連線
            self.start_dot = item
            self.current_line = None
        else:
            # 如果未點擊在小白點上，允許拖動畫布
            self.start_dot = None
            self.current_line = None
            self.last_mouse_pos = event.pos()
        
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """處理鼠標移動事件"""
        if self.start_dot:
            # 動態顯示連線
            if self.current_line:
                self.graphics_scene.removeItem(self.current_line)  # 移除舊的動態線條

            start_pos = self.start_dot.mapToScene(self.start_dot.boundingRect().center())
            end_pos = self.graphics_view.mapToScene(event.pos())
            self.current_line = self.graphics_scene.addLine(
                start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y(), 
                QPen(QColor("lightblue"), 1)
            )
        else:
            # 拖動畫布
            if self.last_mouse_pos:
                delta = event.pos() - self.last_mouse_pos
                self.graphics_view.horizontalScrollBar().setValue(
                    self.graphics_view.horizontalScrollBar().value() - delta.x()
                )
                self.graphics_view.verticalScrollBar().setValue(
                    self.graphics_view.verticalScrollBar().value() - delta.y()
                )
                self.last_mouse_pos = event.pos()
        
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """處理鼠標釋放事件"""
        if self.start_dot:
            # 完成連線
            scene_pos = self.graphics_view.mapToScene(event.pos())
            item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
            if item and item.data(0) == "dot" and item != self.start_dot:
                # 繪製最終連線
                start_pos = self.start_dot.mapToScene(self.start_dot.boundingRect().center())
                end_pos = item.mapToScene(item.boundingRect().center())
                self.graphics_scene.addLine(
                    start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y(), 
                    QPen(QColor("blue"), 2)
                )
            
            # 移除動態線條
            if self.current_line:
                self.graphics_scene.removeItem(self.current_line)
            self.current_line = None
            self.start_dot = None
        else:
            # 完成拖動畫布操作
            self.last_mouse_pos = None
        
        event.accept()

    def wheelEvent(self, event: QWheelEvent):
        """使用滾輪放大縮小圖片"""
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.graphics_view.scale(factor, factor)
