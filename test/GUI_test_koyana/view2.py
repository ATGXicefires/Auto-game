from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QPlainTextEdit, QGraphicsView, QGraphicsScene,
                               QGraphicsRectItem, QFileDialog,
                               QGraphicsPixmapItem, QMenu, QGraphicsLineItem)
from PySide6.QtGui import QPainter, QColor, QPixmap, QPen, QMouseEvent
from PySide6.QtCore import Qt


class View2(QWidget):
    def __init__(self):
        super().__init__()

        # 创建主布局
        main_layout = QVBoxLayout(self)
        # 创建一个按钮和画布的布局容器
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.file_button = QPushButton("選擇文件")
        self.path_display = QPlainTextEdit()
        #self.path_display.setReadOnly(True)
        self.file_button.clicked.connect(self.open_file_dialog)

        left_layout.addWidget(self.file_button)
        left_layout.addWidget(self.path_display)


        # 添加自定義畫布視圖
        self.canvas_view = CanvasView()
        layout.addWidget(self.canvas_view, 3)  # 画布占 3/4
        layout.addLayout(left_layout, 1)  # 按钮区域占 1/4

        # 将布局添加到主窗口
        main_layout.addLayout(layout)


    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇文件")
        if file_path:
            self.path_display.setPlainText(file_path)
class CanvasView(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Initialize the scene that holds all the drawable items.
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Configure the view for smooth rendering and interaction.
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Add a grid to the canvas for visual alignment.
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.base_grid_size = 20  # Set the base grid size.
        self.current_grid_size = self.base_grid_size
        self.add_grid()

        # Variables to handle line drawing
        self.temp_line = None  # Temporary line for drawing
        self.start_item = None  # Start item of the line

    def add_grid(self):
       """Draw grid lines on the scene to aid in alignment."""
       # 移除现有的网格线，而不影响其他项目。
       for item in self.scene.items():
           if isinstance(item, QGraphicsLineItem) and getattr(item, 'is_grid_line', False):
               self.scene.removeItem(item)

       scene_rect = self.scene.sceneRect()

       # 根據縮放因子調整線條粗細
       scale_factor = self.transform().m11()
       pen_color = QColor(200, 200, 200, 100)
       pen = QPen(pen_color)
       pen.setWidthF(1 / scale_factor)

       # 繪製水平線
       y = scene_rect.top()
       while y <= scene_rect.bottom():
           line = self.scene.addLine(scene_rect.left(), y, scene_rect.right(), y, pen)
           line.is_grid_line = True  # 標記為網格線
           y += self.current_grid_size

       # 繪製垂直線
       x = scene_rect.left()
       while x <= scene_rect.right():
           line = self.scene.addLine(x, scene_rect.top(), x, scene_rect.bottom(), pen)
           line.is_grid_line = True  # 標記為網格線
           x += self.current_grid_size

    def add_connection(self, start_item, end_item):
       """Create a connection line between two items."""
       if not start_item or not end_item:
           return

       # 計算起點與終點位置
       start_center = start_item.sceneBoundingRect().center()
       end_center = end_item.sceneBoundingRect().center()

       pen = QPen(QColor(0, 0, 255))  # 藍色箭頭線
       pen.setWidthF(2 / self.view.transform().m11())  # 根據縮放調整線條寬度

       # 添加箭頭線
       line = self.scene.addLine(start_center.x(), start_center.y(), end_center.x(), end_center.y(), pen)
       line.is_connection = True  # 標記為連線

    def update_scene_on_zoom(self):
       """Update all items in the scene during zooming."""
       scale_factor = self.view.transform().m11()

       # 更新網格線
       for item in self.scene.items():
           if isinstance(item, QGraphicsLineItem):
               if getattr(item, 'is_grid_line', False):
                   pen = item.pen()
                   pen.setWidthF(1 / scale_factor)
                   item.setPen(pen)
               elif getattr(item, 'is_connection', False):
                   pen = item.pen()
                   pen.setWidthF(2 / scale_factor)
                   item.setPen(pen)

    #Zoom event integration
    #self.view.viewport().installEventFilter(self)



    def contextMenuEvent(self, event):
        """Display a context menu when the user right-clicks on the canvas."""
        clicked_item = self.itemAt(event.pos())
        if isinstance(clicked_item, QGraphicsPixmapItem):
            menu = QMenu(self)
            add_connection_action = menu.addAction("Add Connection")
            selected_action = menu.exec(event.globalPos())

            if selected_action == add_connection_action:
                self.start_drawing_line(clicked_item)
        else:
            menu = QMenu(self)
            add_image_action = menu.addAction("Add Image")
            selected_action = menu.exec(event.globalPos())

            if selected_action == add_image_action:
                self.add_image()

    def add_image(self):
        """Add an image to the scene at the center of the viewport."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setFlags(QGraphicsPixmapItem.ItemIsMovable | QGraphicsPixmapItem.ItemIsSelectable)

                center_pos = self.mapToScene(self.viewport().rect().center())
                pixmap_item.setPos(center_pos)

                self.scene.addItem(pixmap_item)

    def start_drawing_line(self, start_item):
        """Initialize the line drawing process."""
        self.start_item = start_item
        self.temp_line = QGraphicsLineItem()
        pen = QPen(QColor(0, 0, 255), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.temp_line.setPen(pen)
        self.scene.addItem(self.temp_line)

    def mouseMoveEvent(self, event):
        """Update the temporary line's end point during mouse movement."""
        if self.temp_line and self.start_item:
            start_center = self.start_item.sceneBoundingRect().center()
            end_pos = self.mapToScene(event.pos())
            self.temp_line.setLine(start_center.x(), start_center.y(), end_pos.x(), end_pos.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
       """Finalize the line drawing when the mouse is released."""
       if self.temp_line and self.start_item:
           end_item = self.itemAt(event.pos())
           if isinstance(end_item, QGraphicsPixmapItem) and end_item != self.start_item:
               # Get the center positions of the start and end items
               start_center = self.start_item.sceneBoundingRect().center()
               end_center = end_item.sceneBoundingRect().center()

               # Draw the final line with an arrow
               final_line = QGraphicsLineItem(start_center.x(), start_center.y(), end_center.x(), end_center.y())
               pen = QPen(QColor(0, 0, 255), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
               final_line.setPen(pen)
               self.scene.addItem(final_line)

           # Remove the temporary line
           self.scene.removeItem(self.temp_line)
           self.temp_line = None
           self.start_item = None

       super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
       """Handle zooming in and out using the mouse wheel."""
       zoom_factor = 1.15
       if event.angleDelta().y() > 0:
           self.scale(zoom_factor, zoom_factor)
       else:
           self.scale(1 / zoom_factor, 1 / zoom_factor)

       # Update grid size and redraw
       self.current_grid_size = max(10, min(100, self.base_grid_size * self.transform().m11()))
       self.add_grid()

       # Adjust line thickness for all existing lines
       for item in self.scene.items():
           if isinstance(item, QGraphicsLineItem):
               pen = item.pen()
               pen.setWidthF(2 / self.transform().m11())  # Adjust thickness based on zoom level
               item.setPen(pen)



    # 添加以下代碼以適應視窗範圍
    #self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
