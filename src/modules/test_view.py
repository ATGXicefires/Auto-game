from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QMenu, QGraphicsLineItem, QGraphicsPixmapItem
)
from PySide6.QtGui import (
    QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent,
    QPen, QPainter, QMouseEvent, QContextMenuEvent, QKeyEvent
)
from PySide6.QtCore import Qt, QPointF, QEvent
import shutil
import os
from functions import get_resource_path

class PixmapNode(QGraphicsPixmapItem):
    """
    自訂類別，承載 connections (所有連線)。
    一旦位置改變 (itemChange)，更新所有連線，使線條跟著移動。
    每條連線會記錄：
      (otherNode, lineObj, myOffset, otherOffset)
    myOffset / otherOffset 用來儲存連線端在各自物件中的對應位置（local coordinate）。
    """
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemSendsScenePositionChanges, True)
        # connections: List[ (PixmapNode, QGraphicsLineItem, QPointF, QPointF) ]
        #   → (對象, 線條物件, 我方 local_offset, 對方 local_offset)
        self.connections = []

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange:
            # 當自己的位置改變時，更新所有連線
            for otherNode, lineObj, myOffset, otherOffset in self.connections:
                self.updateLine(lineObj, otherNode, myOffset, otherOffset)
        return super().itemChange(change, value)

    def updateLine(self, lineObj, otherNode, myOffset, theirOffset):
        """
        根據自己和 otherNode 的 offset，各自 mapToScene() 得到實際場景座標，
        並更新線段端點。
        """
        my_point_in_scene = self.mapToScene(myOffset)
        their_point_in_scene = otherNode.mapToScene(theirOffset)
        lineObj.setLine(
            my_point_in_scene.x(), my_point_in_scene.y(),
            their_point_in_scene.x(), their_point_in_scene.y()
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
        self.start_item = None       # 儲存連線起始物件 (PixmapNode)
        self.start_offset = QPointF()  # 儲存點擊在 start_item 上的相對位置
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
        """
        在「連線模式」下，用滑鼠左鍵完成連線。
        暫時線起始點将對應使用者實際點擊的位置 (start_offset)，而非固定在中心。
        """
        if watched == self.graphics_view.viewport() and isinstance(event, QMouseEvent):
            scene_pos = self.graphics_view.mapToScene(event.pos())

            if self.is_connection_mode:
                if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                    item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
                    if isinstance(item, PixmapNode):
                        self.start_item = item
                        self.is_connecting = True

                        # 記錄按下點擊在該 item 上的「本地座標」
                        # mapFromScene()：把「場景座標」轉換到 item 的本地座標系
                        self.start_offset = item.mapFromScene(scene_pos)

                        # 建立暫時線（虛線）
                        self.temp_line = QGraphicsLineItem()
                        pen = QPen(Qt.white)
                        pen.setStyle(Qt.DashLine)
                        pen.setWidth(4)
                        self.temp_line.setPen(pen)
                        self.graphics_scene.addItem(self.temp_line)

                        # 暫時線的端點：從「起始物件上的點擊處」綁定到「當前滑鼠位置」
                        start_scene_pt = item.mapToScene(self.start_offset)
                        self.temp_line.setLine(
                            start_scene_pt.x(),
                            start_scene_pt.y(),
                            scene_pos.x(),
                            scene_pos.y()
                        )

                elif event.type() == QEvent.MouseMove and self.is_connecting and self.temp_line and self.start_item:
                    # 動態更新暫時線
                    start_scene_pt = self.start_item.mapToScene(self.start_offset)
                    self.temp_line.setLine(
                        start_scene_pt.x(),
                        start_scene_pt.y(),
                        scene_pos.x(),
                        scene_pos.y()
                    )

                elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                    # 結束暫時線
                    if self.temp_line:
                        self.graphics_scene.removeItem(self.temp_line)
                        self.temp_line = None

                    if self.is_connecting:
                        end_item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
                        if isinstance(end_item, PixmapNode) and end_item != self.start_item:
                            # 連線成功，同樣記住 end_item 上的對應座標
                            end_offset = end_item.mapFromScene(scene_pos)
                            self.connectTwoItems(self.start_item, self.start_offset,
                                                 end_item, end_offset)
                            self.label.setText("圖片已連線")
                        else:
                            self.label.setText("取消連線")

                    # 重置起始物件狀態
                    self.start_item = None
                    self.is_connecting = False
        return super().eventFilter(watched, event)

    def connectTwoItems(self, itemA: PixmapNode, offsetA: QPointF,
                        itemB: PixmapNode, offsetB: QPointF):
        """
        在場景上繪製「終版連線」的實線，
        並記住彼此連線關係 + 端點相對位置 (offsetA, offsetB)。
        """
        # 將 offsetA / offsetB 轉換成場景座標，確定線起點與終點
        a_in_scene = itemA.mapToScene(offsetA)
        b_in_scene = itemB.mapToScene(offsetB)

        line = QGraphicsLineItem()
        line.setZValue(-1)  # 讓線位於圖片之下
        pen = QPen(Qt.white)
        pen.setWidth(4)
        line.setPen(pen)
        line.setLine(a_in_scene.x(), a_in_scene.y(),
                     b_in_scene.x(), b_in_scene.y())
        self.graphics_scene.addItem(line)

        # 雙向記錄連線：各自存自己的 offset 以及對象的 offset
        itemA.connections.append((itemB, line, offsetA, offsetB))
        itemB.connections.append((itemA, line, offsetB, offsetA))

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

        # 使用 PixmapNode
        pixmap_node = PixmapNode(pixmap)
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
