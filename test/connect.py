from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPixmapItem, QVBoxLayout, QPushButton, QWidget, QMessageBox
from PySide6.QtCore import Qt, QPointF, QLineF, QEvent
from PySide6.QtGui import QPen, QMouseEvent, QPixmap, QDragEnterEvent, QDropEvent
import sys
import os

class Node(QGraphicsEllipseItem):
    def __init__(self, name, x, y, scene):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(Qt.lightGray)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)  # 禁用節點移動
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges, True)
        self.setAcceptDrops(True)  # 啟用拖放

        self.name = name
        self.connections = []  # 儲存連線和對應的線條物件
        self.scene = scene
        self.scene.addItem(self)
        self.pixmap_item = None  # 用於顯示拖放圖片的項目

    def __hash__(self):
        return hash(self.name)

    def connect(self, target_node):
        if target_node in [conn[0] for conn in self.connections]:
            print(f"節點 {self.name} 已經連接到節點 {target_node.name}。")
            return  # 避免重複連接

        line = QGraphicsLineItem(
            self.scenePos().x(), self.scenePos().y(),
            target_node.scenePos().x(), target_node.scenePos().y()
        )
        pen = QPen(Qt.white)
        pen.setWidth(2)
        line.setPen(pen)
        self.scene.addItem(line)
        self.connections.append((target_node, line))  # 同時儲存目標節點和線條

        # 添加反向連接
        target_node.connections.append((self, line))
        print(f"節點 {self.name} 已連接到節點 {target_node.name}。")

    def execute(self, visited=None):
        if visited is None:
            visited = set()

        if self in visited:
            print(f"節點 {self.name} 已被訪問過，跳過以防止迴圈。")
            return

        visited.add(self)
        print(f"執行節點 {self.name}")

        for target_node, _ in self.connections:
            print(f"節點 {self.name} 將執行連接的節點 {target_node.name}")
            target_node.execute(visited)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionChange and self.scene:
            # 更新所有相連的線條
            for target_node, line in self.connections:
                line.setLine(
                    self.scenePos().x(), self.scenePos().y(),
                    target_node.scenePos().x(), target_node.scenePos().y()
                )
        return super().itemChange(change, value)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # 檢查是否包含圖片檔案
            for url in event.mimeData().urls():
                if os.path.splitext(url.toLocalFile())[1].lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):
        self.dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                    pixmap = QPixmap(file_path)
                    if not pixmap.isNull():
                        # 如果已經有圖片，則先移除
                        if self.pixmap_item:
                            self.scene.removeItem(self.pixmap_item)
                        
                        # 調整圖片大小以適應節點
                        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.pixmap_item = QGraphicsPixmapItem(pixmap, self)
                        self.pixmap_item.setOffset(-pixmap.width()/2, -pixmap.height()/2)
                        print(f"節點 {self.name} 已設置圖片: {file_path}")
                        event.acceptProposedAction()
                        return
        event.ignore()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Connection Visualizer")

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.black)
        self.view = GraphicsViewWithPan(self.scene)  # 使用自訂的 GraphicsViewWithPan

        self.add_node_button = QPushButton("新增節點")
        self.add_node_button.clicked.connect(self.add_node)

        self.execute_button = QPushButton("執行")
        self.execute_button.clicked.connect(self.execute_nodes)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.add_node_button)
        self.layout.addWidget(self.execute_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.nodes = []
        self.temp_line = None
        self.start_node = None
        self.is_connecting = False  # 追蹤是否正在連線

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def add_node(self):
        name = f"Node{len(self.nodes) + 1}"
        x, y = 100 + len(self.nodes) * 100, 300
        node = Node(name, x, y, self.scene)
        self.nodes.append(node)
        print(f"新增節點 {name}，位置: ({x}, {y})")

    def execute_nodes(self):
        if not self.nodes:
            QMessageBox.warning(self, "警告", "沒有節點可執行。")
            return

        print("開始執行節點：")
        self.nodes[0].execute()

    def eventFilter(self, source, event):
        if isinstance(event, QMouseEvent):
            scene_pos = self.view.mapToScene(event.pos())

            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                item = self.scene.itemAt(scene_pos, self.view.transform())
                if isinstance(item, Node):
                    self.start_node = item
                    self.is_connecting = True  # 設置連線狀態
                    # 創建預覽線條
                    self.temp_line = QGraphicsLineItem()
                    pen = QPen(Qt.white)
                    pen.setStyle(Qt.DashLine)  # 虛線效果
                    pen.setWidth(2)
                    self.temp_line.setPen(pen)
                    self.scene.addItem(self.temp_line)
                    start_pos = self.start_node.scenePos()
                    self.temp_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())

            elif event.type() == QEvent.MouseMove and self.is_connecting and self.temp_line:
                # 更新預覽線條的終點
                start_pos = self.start_node.scenePos()
                self.temp_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())

            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                if self.temp_line:
                    self.scene.removeItem(self.temp_line)
                    self.temp_line = None

                if self.is_connecting:
                    end_item = self.scene.itemAt(scene_pos, self.view.transform())
                    if isinstance(end_item, Node) and self.start_node and end_item != self.start_node:
                        self.start_node.connect(end_item)

                self.start_node = None
                self.is_connecting = False  # 重置連線狀態

        return super().eventFilter(source, event)

class GraphicsViewWithPan(QGraphicsView):  # 保持畫布可移動
    def __init__(self, scene):
        super().__init__(scene)
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self.setDragMode(QGraphicsView.NoDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan:
            delta_x = event.x() - self._pan_start_x
            delta_y = event.y() - self._pan_start_y
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta_x)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta_y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())