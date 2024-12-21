from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QVBoxLayout, QPushButton, QWidget, QMessageBox
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPen, QMouseEvent
import sys

class Node(QGraphicsEllipseItem):
    def __init__(self, name, x, y, scene):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(Qt.lightGray)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges, True)

        self.name = name
        self.connections = []  # 儲存連線和對應的線條物件
        self.scene = scene
        self.scene.addItem(self)

    def connect(self, target_node):
        line = QGraphicsLineItem(
            self.scenePos().x(), self.scenePos().y(),  # 修正起始點座標
            target_node.scenePos().x(), target_node.scenePos().y()  # 修正終點座標
        )
        pen = QPen(Qt.white)
        pen.setWidth(2)
        line.setPen(pen)
        self.scene.addItem(line)
        self.connections.append((target_node, line))  # 同時儲存目標節點和線條

    def execute(self, visited=None):
        if visited is None:
            visited = set()

        if self in visited:
            print(f"Node {self.name} has already been visited. Skipping to prevent loops.")
            return

        visited.add(self)
        print(f"Executing node {self.name}")

        for connection in self.connections:
            connection.execute(visited)

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionChange and self.scene():
            # 更新所有相連的線條
            for target_node, line in self.connections:
                line.setLine(
                    self.scenePos().x(), self.scenePos().y(),
                    target_node.scenePos().x(), target_node.scenePos().y()
                )
        return super().itemChange(change, value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Connection Visualizer")

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.black)
        self.view = QGraphicsView(self.scene)

        self.add_node_button = QPushButton("Add Node")
        self.add_node_button.clicked.connect(self.add_node)

        self.execute_button = QPushButton("Execute")
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

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def add_node(self):
        name = f"Node{len(self.nodes) + 1}"
        x, y = 100 + len(self.nodes) * 100, 300
        node = Node(name, x, y, self.scene)
        self.nodes.append(node)

    def execute_nodes(self):
        if not self.nodes:
            QMessageBox.warning(self, "Warning", "No nodes to execute.")
            return

        print("Starting execution:")
        self.nodes[0].execute()

    def eventFilter(self, source, event):
        if event.type() == QMouseEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            item = self.scene.itemAt(self.view.mapToScene(event.pos()), self.view.transform())
            if isinstance(item, Node):
                self.start_node = item
                self.temp_line = QGraphicsLineItem(
                    QLineF(item.scenePos().x() + 20, item.scenePos().y() + 20, event.scenePos().x(), event.scenePos().y())
                )
                pen = QPen(Qt.white)
                pen.setStyle(Qt.DashLine)
                self.temp_line.setPen(pen)
                self.scene.addItem(self.temp_line)

        elif event.type() == QMouseEvent.MouseMove and self.temp_line:
            line = self.temp_line.line()
            line.setP2(event.scenePos())
            self.temp_line.setLine(line)

        elif event.type() == QMouseEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None

            item = self.scene.itemAt(self.view.mapToScene(event.pos()), self.view.transform())
            if isinstance(item, Node) and self.start_node and item != self.start_node:
                self.start_node.connect(item)

            self.start_node = None

        return super().eventFilter(source, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
