from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent, QPainter
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
            self.label.setText(f"已載入圖片: {file_name}")

        except Exception as e:
            print(f"處理圖片時發生錯誤: {e}")

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