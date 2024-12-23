from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QMessageBox,
    QMenu
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPointF, QLineF, QEvent
from PySide6.QtGui import QPen, QMouseEvent, QPixmap, QDragEnterEvent, QDropEvent, QPalette, QColor
import sys
import os

class Node(QGraphicsEllipseItem):
    def __init__(self, name, x, y, scene):
        super().__init__(-20, -20, 40, 40)
        self.setPos(x, y)
        self.setBrush(Qt.lightGray)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges, True)
        self.setAcceptDrops(True)  # 啟用拖放

        self.name = name
        self.connections = []  # 儲存連線和對應的線條物件
        self.scene = scene
        self.scene.addItem(self)
        self.pixmap_item = None  # 用於顯示拖放圖片的項目

    def __hash__(self):
        return hash(self.name) # ᛁ ᛞᚩᚾ ᛏ ᚴᚾᚩᚹ ᚹᚻᚨᛏ ᛁᛋ ᛏᚻᛁᛋ ᛚ ᚩ ᛚ

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
        line.setZValue(0)  # 設置連接線的 z-value 較低
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
                            self.pixmap_item = None
                            self.setBrush(Qt.lightGray)  # 恢復原本的刷子顏色

                        # 調整圖片大小以適應節點
                        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.pixmap_item = QGraphicsPixmapItem(pixmap, self)
                        self.pixmap_item.setOffset(-pixmap.width()/2, -pixmap.height()/2)
                        self.pixmap_item.setZValue(1)  # 設置圖片的 z-value 較高
                        print(f"節點 {self.name} 已設置圖片: {file_path}")

                        # 隱藏白點
                        self.setBrush(Qt.transparent)
                        event.acceptProposedAction()
                        return
        event.ignore()

    def contextMenuEvent(self, event):
        """
        當使用者在節點上按下右鍵時觸發。
        這裡建立一組連線清單，讓使用者選擇想連線的對象。
        """
        menu = QMenu()
        # 產生「Connect To」的子選單
        connect_menu = menu.addMenu("Connect to...")
        self.create_connection_menu(connect_menu)

        # 顯示選單，並讓使用者選擇
        menu.exec_(event.screenPos())

    def create_connection_menu(self, menu: QMenu):
        """
        創建所有可能可以連線的節點選項，並將動作綁定到連線函式。
        """
        # 這裡假設我們可從 self.scene.items() (或從 MainWindow 傳進所有節點清單) 取得所有節點
        all_items = self.scene.items()
        for item in all_items:
            if isinstance(item, Node) and item != self:
                node_name = item.name
                action = QAction(f"{node_name}", menu)
                # 連線的邏輯：點擊後呼叫 self.connect(item)
                action.triggered.connect(lambda checked, target_node=item: self.connect(target_node))
                menu.addAction(action)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Connection Visualizer")

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.black)
        self.view = GraphicsViewWithPan(self.scene)

        self.add_node_button = QPushButton("新增節點")
        self.add_node_button.clicked.connect(self.prepare_to_add_node)

        self.execute_button = QPushButton("執行")
        self.execute_button.clicked.connect(self.execute_nodes)

        self.toggle_mode_button = QPushButton("切換至連線模式")
        self.toggle_mode_button.clicked.connect(self.toggle_connection_mode)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.layout.addWidget(self.add_node_button)
        self.layout.addWidget(self.execute_button)
        self.layout.addWidget(self.toggle_mode_button)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.nodes = []
        self.temp_line = None
        self.start_node = None

        self.is_connection_mode = False
        self.is_connecting = False

        # 新增此變數，用來判斷是否要等待滑鼠點擊產生節點
        self.is_adding_node = False

        self.view.setMouseTracking(True)
        self.view.viewport().installEventFilter(self)

    def prepare_to_add_node(self):
        """
        使用者按下「新增節點」按鈕後，準備讓下一次滑鼠左鍵點擊在場景上時新增節點。
        """
        self.is_adding_node = True
        print("請在場景上點擊以新增節點。")

    def add_node_at_position(self, pos: QPointF):
        """
        在指定的場景座標 pos 產生節點
        """
        name = f"Node{len(self.nodes) + 1}"
        node = Node(name, pos.x(), pos.y(), self.scene)
        node.setFlag(QGraphicsEllipseItem.ItemIsMovable, not self.is_connection_mode)
        self.nodes.append(node)
        print(f"新增節點 {name}，位置: ({pos.x()}, {pos.y()})")

    def toggle_connection_mode(self):
        """
        切換「連線模式」與「移動模式」：
        - 連線模式: 節點無法被移動，只能拖曳建立連線
        - 移動模式: 節點可被拖曳移動，無法建立連線
        """
        self.is_connection_mode = not self.is_connection_mode
        if self.is_connection_mode:
            self.toggle_mode_button.setText("切換至移動模式")
            # 關閉節點可移動
            for node in self.nodes:
                node.setFlag(QGraphicsEllipseItem.ItemIsMovable, False)
        else:
            self.toggle_mode_button.setText("切換至連線模式")
            # 開啟節點可移動
            for node in self.nodes:
                node.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)

    def execute_nodes(self):
        if not self.nodes:
            QMessageBox.warning(self, "警告", "沒有節點可執行。")
            return

        print("開始執行節點：")
        self.nodes[0].execute()

    def eventFilter(self, source, event):
        if isinstance(event, QMouseEvent):
            scene_pos = self.view.mapToScene(event.pos())

            # 若正在等候新增節點，且滑鼠左鍵點擊
            if (event.type() == QEvent.MouseButtonPress 
                and event.button() == Qt.LeftButton
                and self.is_adding_node):
                self.add_node_at_position(scene_pos)
                self.is_adding_node = False
                return True  # 已處理此事件

            # 以下原本的連線模式事件邏輯保持
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                if self.is_connection_mode:
                    item = self.scene.itemAt(scene_pos, self.view.transform())
                    if isinstance(item, Node):
                        self.start_node = item
                        self.is_connecting = True
                        self.temp_line = QGraphicsLineItem()
                        pen = QPen(Qt.white)
                        pen.setStyle(Qt.DashLine)
                        pen.setWidth(2)
                        self.temp_line.setPen(pen)
                        self.scene.addItem(self.temp_line)
                        start_pos = self.start_node.scenePos()
                        self.temp_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())

            elif event.type() == QEvent.MouseMove and self.is_connection_mode and self.temp_line and self.start_node:
                start_pos = self.start_node.scenePos()
                self.temp_line.setLine(start_pos.x(), start_pos.y(), scene_pos.x(), scene_pos.y())

            elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
                if self.is_connection_mode:
                    if self.temp_line:
                        self.scene.removeItem(self.temp_line)
                        self.temp_line = None

                    if self.is_connecting:
                        end_item = self.scene.itemAt(scene_pos, self.view.transform())
                        if isinstance(end_item, Node) and self.start_node and end_item != self.start_node:
                            self.start_node.connect(end_item)

                    self.start_node = None
                    self.is_connecting = False

        return super().eventFilter(source, event)

class GraphicsViewWithPan(QGraphicsView):  # 保持畫布可移動
    def __init__(self, scene):
        super().__init__(scene)
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._space_pressed = False  # 用來追蹤是否按住空白鍵
        self.setDragMode(QGraphicsView.NoDrag)

        # 若要讓視圖能接收鍵盤事件，需設定適當的 FocusPolicy
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        # 偵測是否按住空白鍵
        if event.key() == Qt.Key_Space:
            self._space_pressed = True
            # 當按住空白鍵時，如果還沒開始拖曳，顯示OpenHandCursor」
            if not self._pan:
                self.setCursor(Qt.OpenHandCursor)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        # 偵測是否放開空白鍵
        if event.key() == Qt.Key_Space:
            self._space_pressed = False
            # 如果當前非拖曳中，回復預設游標
            if not self._pan:
                self.setCursor(Qt.ArrowCursor)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # 原本就有的中鍵拖曳邏輯
            self._pan = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(Qt.ClosedHandCursor)
        # 新增邏輯：如果按住空白鍵 + 左鍵，也可以平移畫布
        elif self._space_pressed and event.button() == Qt.LeftButton:
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
        # 當放開中鍵或左鍵時，結束拖曳
        if self._pan and (event.button() == Qt.MiddleButton or event.button() == Qt.LeftButton):
            self._pan = False
            # 如果空白鍵仍按住時，顯示「OpenHandCursor，否則回到箭頭游標
            self.setCursor(Qt.OpenHandCursor if self._space_pressed else Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        # 如果按住 Ctrl 鍵，執行縮放，否則維持原行為
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            zoom_in_factor = 1.25
            zoom_out_factor = 1 / zoom_in_factor
            if event.angleDelta().y() > 0:
                # 向上滾動 -> 放大
                self.scale(zoom_in_factor, zoom_in_factor)
                # 向下滾動 -> 縮小
            else:
            # 若沒有按住 Ctrl，則繼續執行預設的滾輪事件
                self.scale(zoom_out_factor, zoom_out_factor)
        else:
            super().wheelEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. 設定 Fusion 風格
    app.setStyle("Fusion")

    # 2. 設定深色主題的 Palette（可自由調整色票）
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    # 3. 使用 StyleSheet 進一步修飾（可自行增減需要的元件樣式）
    app.setStyleSheet("""
        QWidget {
            font-family: "Microsoft JhengHei";
            font-size: 14px;
        }
        QToolTip {
            color: #ffffff;
            background-color: #2a2a2a;
            border: 1px solid #3d3d3d;
        }
        QPushButton {
            background-color: #5c5c5c;
            border-radius: 4px;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #6c6c6c;
        }
        QGraphicsView {
            border: 1px solid #3d3d3d;
        }
        QMessageBox {
            background-color: #353535;
        }
    """)

    window = MainWindow()
    window.resize(1280, 720)
    window.show()
    sys.exit(app.exec())
