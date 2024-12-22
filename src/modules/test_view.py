from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtGui import (
    QPixmap, QDragEnterEvent, QDropEvent,
    QPainter, QFont, QDrag, QMouseEvent, QPen
)
from PySide6.QtCore import Qt, QMimeData, QUrl, QPointF
import os
import shutil
from functions import get_resource_path

class DraggableLabel(QLabel):
    """
    置於左側工具列的可拖曳標籤（pictures/pictures.png）。
    使用者可將此標籤拖動到 QGraphicsView 中，以產生可再接收其他圖片的容器。
    """
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        # 使用 get_resource_path 取得打包後的正確路徑
        self.image_path = get_resource_path(image_path)
        # 將圖片縮小為 100 x 100（維持比例）
        pixmap = QPixmap(self.image_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        # 固定顯示區域為 (100, 100)
        self.setFixedSize(100, 100)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()

            abs_path = os.path.abspath(self.image_path)
            file_url = QUrl.fromLocalFile(abs_path)
            mime_data.setUrls([file_url])

            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap())  # 拖曳效果顯示的圖
            drag.exec(Qt.CopyAction | Qt.MoveAction)
        else:
            super().mousePressEvent(event)

class ContainerPixmapItem(QGraphicsPixmapItem):
    """
    當使用者將 pictures/pictures.png 拖到畫布後，建立的可接收其他圖片的容器。
    此類別將自身設定為可拖放，並在 dropEvent 中更新為新圖片。
    """
    def __init__(self, pixmap):
        super().__init__(pixmap)
        # 設定可移動、可選取
        self.setFlags(
            QGraphicsPixmapItem.ItemIsMovable |
            QGraphicsPixmapItem.ItemIsSelectable
        )
        # 接受拖放
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 檢查是否為圖片檔案
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                _, ext = os.path.splitext(url.toLocalFile())
                if ext.lower() in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        # 若為圖片檔案，替換當前顯示的圖
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif")
            ):
                # 複製到 detect 資料夾後，更新 pixmap
                detect_folder = get_resource_path('detect')
                if not os.path.exists(detect_folder):
                    os.makedirs(detect_folder)

                file_name = os.path.basename(file_path)
                destination_path = os.path.join(detect_folder, file_name)
                shutil.copy(file_path, destination_path)

                new_pix = QPixmap(destination_path)
                if not new_pix.isNull():
                    self.setPixmap(new_pix)
        event.acceptProposedAction()

class TestView(QWidget):
    def __init__(self, parent=None):
        """
        初始化視窗與佈局，設定預設參數、拖放屬性，以及建立介面元素。
        """
        super().__init__(parent)
        self.setAcceptDrops(True)

        # 建立主佈局，左側為工具列，右側為畫布
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # 左側工具列
        left_bar = QVBoxLayout()
        main_layout.addLayout(left_bar)

        # 左側最上方放置可拖曳的圖片（pictures.png）
        self.draggable_pictures = DraggableLabel("pictures/pictures.png", self)
        left_bar.addWidget(self.draggable_pictures, 0, Qt.AlignTop)

        # 右側 QGraphicsView + QGraphicsScene
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.graphics_view = QGraphicsView(self)
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        right_layout.addWidget(self.graphics_view)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        覆寫拖入事件：若拖入對象包含檔案，則接受該拖入動作。
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """
        覆寫放下事件：
        1. 若為 pictures.png，則在滑鼠釋放位置建立可接收其他圖片的 ContainerPixmapItem。
        2. 其他圖片檔則直接在畫布中顯示。
        """
        # 取得放開滑鼠時對應 scene 的座標
        mouse_pos_in_scene = self.graphics_view.mapToScene(event.position().toPoint())

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith(
                (".png", ".jpg", ".jpeg", ".bmp", ".gif")
            ):
                file_name = os.path.basename(file_path).lower()

                if file_name == "pictures.png":
                    # 建立可接收後續圖片的容器
                    self.create_container_item(file_path, mouse_pos_in_scene)
                else:
                    self.handle_image_drop(file_path, mouse_pos_in_scene)

    def create_container_item(self, file_path: str, scene_pos: QPointF):
        """
        在畫布中建立可後續接收拖放圖片的容器 (pictures.png)。
        """
        detect_folder = get_resource_path('detect')
        if not os.path.exists(detect_folder):
            os.makedirs(detect_folder)

        file_name = os.path.basename(file_path)
        destination_path = os.path.join(detect_folder, file_name)
        shutil.copy(file_path, destination_path)

        pixmap = QPixmap(destination_path)
        if pixmap.isNull():
            return

        container_item = ContainerPixmapItem(pixmap)
        container_item.setPos(scene_pos)
        self.graphics_scene.addItem(container_item)

    def handle_image_drop(self, file_path: str, scene_pos: QPointF):
        """
        一般圖片加入到 scene 中，可移動、可選取。
        """
        detect_folder = get_resource_path('detect')
        if not os.path.exists(detect_folder):
            os.makedirs(detect_folder)

        file_name = os.path.basename(file_path)
        destination = os.path.join(detect_folder, file_name)
        shutil.copy(file_path, destination)

        pixmap = QPixmap(destination)
        if pixmap.isNull():
            return

        image_item = self.graphics_scene.addPixmap(pixmap)
        image_item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        image_item.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        image_item.setPos(scene_pos)
