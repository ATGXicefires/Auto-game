from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent, QPen, QColor, QPainter, QMouseEvent
from PySide6.QtCore import Qt
import shutil
import os
import sys
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

        # 用於存儲連線的起始點
        self.start_dot = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("拖曳進入事件被接受")
        else:
            event.ignore()
            print("拖曳進入事件被忽略")

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                print(f"拖曳的文件路徑: {file_path}")
                if not file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                    print("拖曳的文件不是支持的圖片格式")
                    continue
                self.handle_image_drop(file_path)
            else:
                print("無效的文件路徑")

    def handle_image_drop(self, file_path):
        try:
            detect_folder = get_resource_path('detect')
            if not os.path.exists(detect_folder):
                os.makedirs(detect_folder)
                print(f"創建資料夾: {detect_folder}")

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(detect_folder, file_name)
            shutil.copy(file_path, destination_path)
            print(f"文件已複製到: {destination_path}")

            # 加載並顯示圖片
            pixmap = QPixmap(destination_path)
            if pixmap.isNull():
                print("無法加載圖片，檢查圖片文件是否損壞")
                return

            # 創建可移動的圖片項目
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)  # 設置圖片為可移動
            pixmap_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)  # 設置圖片為可選擇
            self.graphics_scene.addItem(pixmap_item)

            # 添加小白點
            self.add_white_dots(pixmap_item)

            self.label.setText(f"已載入圖片: {file_name}")

        except Exception as e:
            print(f"處理圖片時發生錯誤: {e}")

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
        top_dot.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        top_dot.setData(0, "dot")  # 標記為小白點
        self.graphics_scene.addItem(top_dot)

        # 下
        bottom_dot = QGraphicsRectItem(rect.width() / 2 - rect_size / 2, rect.height() - rect_size / 2 + offset, rect_size, rect_size, pixmap_item)
        bottom_dot.setPen(pen)
        bottom_dot.setBrush(QColor("white"))
        bottom_dot.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        bottom_dot.setData(0, "dot")
        self.graphics_scene.addItem(bottom_dot)

        # 左
        left_dot = QGraphicsRectItem(-rect_size / 2 - offset, rect.height() / 2 - rect_size / 2, rect_size, rect_size, pixmap_item)
        left_dot.setPen(pen)
        left_dot.setBrush(QColor("white"))
        left_dot.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        left_dot.setData(0, "dot")
        self.graphics_scene.addItem(left_dot)

        # 右
        right_dot = QGraphicsRectItem(rect.width() - rect_size / 2 + offset, rect.height() / 2 - rect_size / 2, rect_size, rect_size, pixmap_item)
        right_dot.setPen(pen)
        right_dot.setBrush(QColor("white"))
        right_dot.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        right_dot.setData(0, "dot")
        self.graphics_scene.addItem(right_dot)

    def mousePressEvent(self, event: QMouseEvent):
        """處理小白點的點擊事件"""
        item = self.graphics_scene.itemAt(self.graphics_view.mapToScene(event.pos()), self.graphics_view.transform())
        if item and item.data(0) == "dot":
            if self.start_dot is None:
                self.start_dot = item
            else:
                # 繪製連線
                start_pos = self.start_dot.mapToScene(self.start_dot.boundingRect().center())
                end_pos = item.mapToScene(item.boundingRect().center())
                line = self.graphics_scene.addLine(start_pos.x(), start_pos.y(),
                                                   end_pos.x(), end_pos.y(),
                                                   QPen(QColor("lightblue"), 2))
                self.start_dot = None  # 重置起始點

    def wheelEvent(self, event: QWheelEvent):
        """使用滾輪放大縮小圖片"""
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        # 檢查是否有選中的圖片
        selected_items = self.graphics_scene.selectedItems()
        if selected_items:
            for item in selected_items:
                item.setScale(item.scale() * factor)
        else:
            self.graphics_view.scale(factor, factor)