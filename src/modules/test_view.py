from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QMenu, QGraphicsLineItem, QGraphicsPixmapItem
)
from PySide6.QtGui import (
    QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent,
    QPen, QPainter, QMouseEvent, QContextMenuEvent, QKeyEvent
)
from PySide6.QtCore import Qt, QPointF, QEvent, QRectF
import shutil
import os
from functions import get_resource_path

class PixmapNode(QGraphicsPixmapItem):
    """
    自訂類別，承載 connections (所有連線)。
    一旦位置改變，即更新每一條連線，使線條跟著移動。
    """
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemSendsScenePositionChanges, True)
        self.connections = []  # [(另一個 PixmapNode, QGraphicsLineItem), ...]

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange:
            # 當圖片位置變化時，更新所有連線
            for otherNode, lineObj in self.connections:
                self.updateLine(lineObj, otherNode)
        return super().itemChange(change, value)

    def updateLine(self, lineObj, otherNode):
        """
        根據自己 (self) 與 otherNode 的「中心座標」，更新 lineObj 的線段位置。
        """
        my_center = self.sceneBoundingRect().center()
        my_center_in_scene = self.mapToScene(my_center)

        other_center = otherNode.sceneBoundingRect().center()
        other_center_in_scene = otherNode.mapToScene(other_center)

        lineObj.setLine(
            my_center_in_scene.x(), my_center_in_scene.y(),
            other_center_in_scene.x(), other_center_in_scene.y()
        )

class TestView(QWidget):
    def __init__(self, parent=None):
        super(TestView, self).__init__(parent)
        self.setAcceptDrops(True)  # 啟用拖放功能

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # 場景與視圖
        self.graphics_view = CustomGraphicsView()
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        main_layout.addWidget(self.graphics_view)

        # 提示標籤
        self.label = QLabel("拖曳圖片到此區域", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16, QFont.Bold))
        self.label.setStyleSheet("color: white; background-color: darkblue; padding: 10px;")
        main_layout.addWidget(self.label)

        # 連線模式
        self.is_connection_mode = False
        self.is_connecting = False
        self.start_item = None  # PixmapNode
        self.temp_line = None

        # 監聽事件
        self.graphics_view.viewport().installEventFilter(self)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)
        if self.is_connection_mode:
            toggle_action = menu.addAction("停止連線模式")
        else:
            toggle_action = menu.addAction("啟用連線模式")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == toggle_action:
            self.toggleConnectionMode()
        event.accept()

    def toggleConnectionMode(self):
        self.is_connection_mode = not self.is_connection_mode
        if self.is_connection_mode:
            self.label.setText("連線模式：點選圖片並拖曳到另一張圖片，以建立連線")
            for item in self.graphics_scene.items():
                if isinstance(item, PixmapNode):
                    item.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
        else:
            self.label.setText("一般模式：拖曳圖片或場景")
            for item in self.graphics_scene.items():
                if isinstance(item, PixmapNode):
                    item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

    def eventFilter(self, watched, event):
        if watched == self.graphics_view.viewport() and isinstance(event, QMouseEvent):
            scene_pos = self.graphics_view.mapToScene(event.pos())

            if self.is_connection_mode:
                if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                    item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
                    if isinstance(item, PixmapNode):
                        self.start_item = item
                        self.is_connecting = True
                        # 建立暫時線
                        self.temp_line = QGraphicsLineItem()
                        pen = QPen(Qt.white)
                        pen.setStyle(Qt.DashLine)
                        pen.setWidth(4)
                        self.temp_line.setPen(pen)
                        self.graphics_scene.addItem(self.temp_line)

                        start_center = self.start_item.sceneBoundingRect().center()
                        start_center_in_scene = self.start_item.mapToScene(start_center)
                        self.temp_line.setLine(
                            start_center_in_scene.x(),
                            start_center_in_scene.y(),
                            scene_pos.x(),
                            scene_pos.y()
                        )

                elif event.type() == QEvent.MouseMove and self.is_connecting and self.temp_line and self.start_item:
                    start_center = self.start_item.sceneBoundingRect().center()
                    start_center_in_scene = self.start_item.mapToScene(start_center)
                    self.temp_line.setLine(
                        start_center_in_scene.x(),
                        start_center_in_scene.y(),
                        scene_pos.x(),
                        scene_pos.y()
                    )

                elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                    if self.temp_line:
                        self.graphics_scene.removeItem(self.temp_line)
                        self.temp_line = None
                    if self.is_connecting:
                        end_item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
                        if isinstance(end_item, PixmapNode) and end_item != self.start_item:
                            self.connectTwoItems(self.start_item, end_item)
                            self.label.setText("圖片已連線")
                        else:
                            self.label.setText("取消連線")
                    self.start_item = None
                    self.is_connecting = False
        return super().eventFilter(watched, event)

    def connectTwoItems(self, itemA: PixmapNode, itemB: PixmapNode):
        """
        在場景上繪製實線，並雙向紀錄連線。
        """
        a_center_in_scene = itemA.mapToScene(itemA.boundingRect().center())
        b_center_in_scene = itemB.mapToScene(itemB.boundingRect().center())

        line = QGraphicsLineItem()
        line.setZValue(-1)
        pen = QPen(Qt.white)
        pen.setWidth(4)
        line.setPen(pen)
        line.setLine(a_center_in_scene.x(), a_center_in_scene.y(),
                     b_center_in_scene.x(), b_center_in_scene.y())
        self.graphics_scene.addItem(line)

        # 雙向記錄連線
        itemA.connections.append((itemB, line))
        itemB.connections.append((itemA, line))

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

        # 使用 PixmapNode 而非 QGraphicsPixmapItem
        pixmap_node = PixmapNode(pixmap)
        # 依目前模式，決定是否可拖曳
        pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsMovable, not self.is_connection_mode)
        pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)

        self.graphics_scene.addItem(pixmap_node)

        self.label.setText(f"已載入圖片: {file_name}")

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.graphics_view.scale(factor, factor)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
