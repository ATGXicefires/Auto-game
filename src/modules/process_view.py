import math
import shutil
import os
import json
import time
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene,
    QMenu, QGraphicsLineItem, QGraphicsPixmapItem, QGraphicsPolygonItem,
    QListWidget, QPushButton, QMessageBox, QInputDialog, QLineEdit, QDialog,
    QDialogButtonBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtGui import (
    QPixmap, QDragEnterEvent, QDropEvent, QFont, QWheelEvent,
    QPen, QPainter, QMouseEvent, QContextMenuEvent, QKeyEvent,
    QPolygonF, QDrag, QColor, QIcon
)
from PySide6.QtCore import (
    Qt, QPointF, QEvent, QMimeData, QUrl
)
from functions import get_resource_path
from log_view import LogView

class ArrowItem(QGraphicsPolygonItem):
    """
    小箭頭形狀，原點在箭頭尖端，往負 X 方向延伸。
    這樣在旋轉時，0 度即指向右邊，角度沿逆時針方向正增。
    """
    def __init__(self):
        super().__init__()
        arrow_shape = QPolygonF([
            QPointF(0, 0),
            QPointF(-15, -8),
            QPointF(-15, 8)
        ])
        self.setPolygon(arrow_shape)
        self.setBrush(Qt.white)
        self.setPen(QPen(Qt.white))

class DraggableListWidget(QListWidget):
    """自訂可拖放的列表元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        
    def startDrag(self, supportedActions):
        """當使用者從列表拖動項目時觸發"""
        item = self.currentItem()
        if not item:
            return
            
        mime_data = QMimeData()
        # 使用完整路徑建立 URL
        file_path = os.path.join(get_resource_path('detect'), item.text())
        url = QUrl.fromLocalFile(file_path)
        mime_data.setUrls([url])
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)

class PixmapNode(QGraphicsPixmapItem):
    """
    自訂類別，承載 connections (所有連線)。
    一旦位置改變 (itemChange)，更新所有連線，使線條跟著移動。
    connections: List[ (otherNode, lineObj, arrowObj, myOffset, otherOffset) ]
       → (對方的 PixmapNode, 連線物件, 箭頭物件, 我方 local_offset, 對方 local_offset)
    """
    def __init__(self, pixmap, file_path):
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemSendsScenePositionChanges, True)
        self.connections = []
        self.file_path = file_path  # 儲存圖片路徑，方便之後需要

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange:
            # 更新所有以此節點為起點或終點的連線
            for otherNode, lineObj, arrowObj, myOffset, otherOffset in self.connections:
                # 如果我是起點（有箭頭），用我的更新方法
                if arrowObj:
                    self.updateLineAndArrow(lineObj, arrowObj, otherNode, myOffset, otherOffset)
                # 如果我是終點（無箭頭），用對方的更新方法
                else:
                    # 在對方的連線列表中找到對應的連線
                    for other_conn in otherNode.connections:
                        if other_conn[0] == self and other_conn[2]:  # 找到指向我的連線
                            otherNode.updateLineAndArrow(lineObj, other_conn[2], self, otherOffset, myOffset)
                            break
        return super().itemChange(change, value)

    def updateLineAndArrow(self, lineObj, arrowObj, otherNode, myOffset, theirOffset):
        """
        動態更新線條端點和箭頭位置與角度，使其指向「由自己 → otherNode」。
        """
        my_point_in_scene = self.mapToScene(myOffset)
        their_point_in_scene = otherNode.mapToScene(theirOffset)

        # 更新線條
        lineObj.setLine(
            my_point_in_scene.x(), my_point_in_scene.y(),
            their_point_in_scene.x(), their_point_in_scene.y()
        )

        # 只有當箭頭物件存在時才更新箭頭
        if arrowObj:
            # 更新箭頭位置和角度
            mid_x = (my_point_in_scene.x() + their_point_in_scene.x()) / 2
            mid_y = (my_point_in_scene.y() + their_point_in_scene.y()) / 2
            arrowObj.setPos(mid_x, mid_y)

            # 算出角度，atan2(dy, dx) 傳回弧度，轉度數後再套用
            dx = their_point_in_scene.x() - my_point_in_scene.x()
            dy = their_point_in_scene.y() - my_point_in_scene.y()
            angle_deg = math.degrees(math.atan2(dy, dx))
            arrowObj.setRotation(angle_deg)

    def mousePressEvent(self, event):
        """當圖片被點擊時觸發"""
        # 取得 ProcessView 實例
        scene = self.scene()
        if scene and scene.views():
            view = scene.views()[0]
            if isinstance(view.parent(), ProcessView):
                process_view = view.parent()
                file_name = os.path.basename(self.file_path)
                process_view.label.setText(f"已選擇圖片: {file_name}")
        
        # 確保事件繼續傳遞
        event.accept()
        super().mousePressEvent(event)

class ProcessView(QWidget):
    def __init__(self, parent=None, log_view=None):
        super(ProcessView, self).__init__(parent)
        self.log_view = None
        if hasattr(parent, 'log_view'):
            self.log_view = parent.log_view
        
        self.setAcceptDrops(True)  # 啟用拖放功能
        
        # 整體使用水平佈局，左側為圖片列表，右側為原本場景與標籤
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # 左側面板 - 使用自訂的可拖放列表
        self.left_panel = QVBoxLayout()
        self.list_label = QLabel("已匯入圖片", self)
        self.list_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.list_label.setAlignment(Qt.AlignCenter)

        self.list_widget = DraggableListWidget(self)  # 使用自訂列表
        self.left_panel.addWidget(self.list_label)
        self.left_panel.addWidget(self.list_widget)

        # 左側佈局加入到整體
        left_container = QWidget()
        left_container.setLayout(self.left_panel)
        main_layout.addWidget(left_container, 0)  # 權重較小

        # 右側主要顯示區域
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.graphics_view = CustomGraphicsView()
        self.graphics_scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)

        # 標籤
        self.label = QLabel("拖曳圖片到此區域", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16, QFont.Bold))
        self.label.setStyleSheet("color: white; background-color: darkblue; padding: 10px;")

        # 連線模式
        self.is_connection_mode = False
        self.is_connecting = False
        self.start_item = None       # 儲存連線起始 PixmapNode
        self.start_offset = QPointF()  # 該 PixmapNode 上的 local offset
        self.temp_line = None

        # 監聽事件
        self.graphics_view.viewport().installEventFilter(self)

        # 右側佈局 - 先排放 View，再排放標籤
        right_layout.addWidget(self.graphics_view, 1)
        right_layout.addWidget(self.label)
        main_layout.addWidget(right_container, 1)  # 權重較大

        # 建立按鈕容器
        self.button_container = QWidget()
        button_layout = QHBoxLayout(self.button_container)
        
        # 添加保存按鈕
        self.save_button = QPushButton("保存連線關係", self)
        self.save_button.clicked.connect(self.save_connections)
        button_layout.addWidget(self.save_button)
        
        # 添加載入按鈕
        self.load_button = QPushButton("載入連線關係", self)
        self.load_button.clicked.connect(self.reload_connections)
        button_layout.addWidget(self.load_button)
        
        # 添加清空按鈕
        self.clear_button = QPushButton("清空連線關係", self)
        self.clear_button.clicked.connect(self.clear_connections)
        button_layout.addWidget(self.clear_button)
        
        # 將按鈕容器加入左側面板
        self.left_panel.addWidget(self.button_container)

        # 使用 get_resource_path 處理所有檔案路徑
        self.detect_folder = get_resource_path('detect')
        self.save_data_folder = get_resource_path('SaveData')
        
        if self.log_view:
            self.log_view.append_log("流程視圖已初始化")

    def contextMenuEvent(self, event: QContextMenuEvent):
        # 獲取點擊位置的場景座標
        scene_pos = self.graphics_view.mapToScene(self.graphics_view.mapFromParent(event.pos()))
        item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
        
        menu = QMenu(self)
        
        # 如果點擊到的是圖片節點或有圖片被選中，添加屬性和刪除選項
        selected_items = [item for item in self.graphics_scene.selectedItems() 
                         if isinstance(item, PixmapNode)]
        
        if isinstance(item, PixmapNode) or selected_items:
            # 添加屬性選項及其子選單
            properties_menu = menu.addMenu("屬性")
            
            # 點擊設定子選單
            click_settings_menu = properties_menu.addMenu("點擊設定")
            
            # 尋找時限設定
            timeout_action = click_settings_menu.addAction("尋找時限")
            timeout_action.triggered.connect(lambda: self.show_timeout_settings(item if isinstance(item, PixmapNode) else selected_items[0]))
            
            # 重複點擊設定
            repeat_action = click_settings_menu.addAction("重複點擊")
            repeat_action.triggered.connect(lambda: self.show_repeat_settings(item if isinstance(item, PixmapNode) else selected_items[0]))
            
            # 圖片詳細資料
            detail_action = properties_menu.addAction("圖片詳細資料")
            detail_action.triggered.connect(lambda: self.show_detail_settings(item if isinstance(item, PixmapNode) else selected_items[0]))
            
            # 其他
            other_action = properties_menu.addAction("其他設定")
            other_action.triggered.connect(lambda: self.show_other_settings(item if isinstance(item, PixmapNode) else selected_items[0]))
            
            menu.addSeparator()  # 添加分隔線
            
            # 原有的刪除選項
            delete_action = menu.addAction("刪除圖片")
            # 如果直接點擊到圖片，刪除該圖片；否則刪除所有選中的圖片
            if isinstance(item, PixmapNode):
                delete_action.triggered.connect(lambda: self.delete_image(item))
            else:
                delete_action.triggered.connect(lambda: self.delete_selected_images(selected_items))
            menu.addSeparator()  # 添加分隔線
        
        # 原有的連線模式切換選項
        if self.is_connection_mode:
            toggle_action = menu.addAction("停止連線模式")
        else:
            toggle_action = menu.addAction("啟用連線模式")
        
        menu.addSeparator()  # 添加分隔線
        
        # 添加清空畫布選項（移到最後）
        clear_action = menu.addAction("清空畫布")
        clear_action.setProperty("class", "danger")  # 設定特殊的 class 屬性
        clear_action.triggered.connect(self.clear_canvas)
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == toggle_action:
            self.toggleConnectionMode()
        
        event.accept()

    def show_timeout_settings(self, item: PixmapNode):
        """顯示尋找時限設定"""
        dialog = QDialog(self)
        dialog.setWindowTitle("尋找時限設定")
        layout = QVBoxLayout()
        
        # 超時設定
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("等待超時（秒）：")
        timeout_spinbox = QSpinBox()
        timeout_spinbox.setRange(1, 16777216)
        timeout_spinbox.setValue(item.timeout if hasattr(item, 'timeout') else 30)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(timeout_spinbox)
        
        # 確認按鈕
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(timeout_layout)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            item.timeout = timeout_spinbox.value()
            self.update_json_timeout(item)

    def show_repeat_settings(self, item: PixmapNode):
        """顯示重複點擊設定"""
        dialog = QDialog(self)
        dialog.setWindowTitle("重複點擊設定")
        layout = QVBoxLayout()
        
        # 重複次數設定
        repeat_layout = QHBoxLayout()
        repeat_label = QLabel("點擊次數：")
        repeat_spinbox = QSpinBox()
        repeat_spinbox.setRange(1, 100)
        repeat_spinbox.setValue(item.repeat_clicks if hasattr(item, 'repeat_clicks') else 1)
        repeat_layout.addWidget(repeat_label)
        repeat_layout.addWidget(repeat_spinbox)
        
        # 點擊間隔設定
        interval_layout = QHBoxLayout()
        interval_label = QLabel("點擊間隔（秒）：")
        interval_spinbox = QDoubleSpinBox()
        interval_spinbox.setRange(0.1, 60.0)
        interval_spinbox.setSingleStep(0.1)
        interval_spinbox.setValue(item.click_interval if hasattr(item, 'click_interval') else 1)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(interval_spinbox)
        
        # 確認按鈕
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(repeat_layout)
        layout.addLayout(interval_layout)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            item.repeat_clicks = repeat_spinbox.value()
            item.click_interval = interval_spinbox.value()
            self.update_json_click_settings(item)

    def update_json_click_settings(self, item):
        """更新 JSON 中的點擊設定"""
        try:
            save_data_path = get_resource_path('SaveData')
            json_files = [f for f in os.listdir(save_data_path) if f.endswith('.json')]
            
            if not json_files:
                if self.log_view:
                    self.log_view.append_log("找不到任何 JSON 檔案")
                return
            
            # 如果有多個檔案，讓使用者選擇
            if len(json_files) > 1:
                file_name, ok = QInputDialog.getItem(
                    self,
                    "選擇檔案",
                    "請選擇要更新的檔案：",
                    json_files,
                    0,
                    False
                )
                if not ok:
                    return
            else:
                file_name = json_files[0]
            
            json_path = os.path.join(save_data_path, file_name)
            
            # 讀取 JSON 檔案
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 取得目標檔案名稱
            target_file = os.path.basename(item.file_path)
            
            # 在 steps 中找到對應的步驟並更新設定
            if 'steps' in data:
                updated = False
                for step_data in data['steps'].values():
                    if isinstance(step_data, dict):
                        if step_data.get('location', '').endswith(target_file):
                            step_data['repeat_clicks'] = item.repeat_clicks
                            step_data['click_interval'] = item.click_interval
                            updated = True
                    elif isinstance(step_data, str) and step_data.endswith(target_file):
                        # 如果是舊格式，轉換為新格式
                        step_data = {
                            'location': step_data,
                            'repeat_clicks': item.repeat_clicks,
                            'click_interval': item.click_interval
                        }
                        updated = True
                
                if updated:
                    # 保存更新後的 JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    if self.log_view:
                        self.log_view.append_log(f"已更新節點 {target_file} 的點擊設定")
                else:
                    if self.log_view:
                        self.log_view.append_log(f"在 JSON 中找不到對應的節點：{target_file}")
            
        except Exception as e:
            if self.log_view:
                self.log_view.append_log(f"更新點擊設定時發生錯誤：{str(e)}")

    def show_detail_settings(self, item: PixmapNode):
        """顯示圖片詳細資料"""
        file_name = os.path.basename(item.file_path)
        file_path = item.file_path
        pos = item.pos()
        
        # 取得檔案資訊
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size / 1024  # 轉換為 KB
        file_modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                    time.localtime(file_stats.st_mtime))
        
        # 取得圖片資訊
        pixmap = item.pixmap()
        width = pixmap.width()
        height = pixmap.height()
        
        # 計算連線資訊
        outgoing_connections = sum(1 for conn in item.connections if conn[2])  # 有箭頭的連線
        incoming_connections = sum(1 for conn in item.connections if not conn[2])  # 無箭頭的連線
        
        # 取得時限資訊
        timeout = getattr(item, 'timeout', 30)  # 如果沒有設定，預設為 30 秒
        
        # 取得重複點擊設定
        repeat_clicks = getattr(item, 'repeat_clicks', 1)  # 如果沒有設定，預設為 1 次
        click_interval = getattr(item, 'click_interval', 1)  # 如果沒有設定，預設為 1 秒
        
        # 建立詳細資訊文字
        detail_text = (
            f"檔案名稱：{file_name}\n"
            f"檔案路徑：{file_path}\n"
            f"檔案大小：{file_size:.2f} KB\n"
            f"修改時間：{file_modified}\n"
            f"\n"
            f"圖片尺寸：{width} x {height}\n"
            f"場景位置：({pos.x():.2f}, {pos.y():.2f})\n"
            f"\n"
            f"點擊設定：\n"
            f"  ➤ 等待時限：{timeout} 秒\n"
            f"  ➤ 重複點擊：{repeat_clicks} 次\n"
            f"  ➤ 點擊間隔：{click_interval} 秒\n"
            f"\n"
            f"連線資訊：\n"
            f"  ➤ 輸出連線：{outgoing_connections}\n"
            f"  ➤ 輸入連線：{incoming_connections}\n"
            f"  ➤ 總連線數：{len(item.connections)}"
        )
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"詳細資訊 - {file_name}")
        msg.setText(detail_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def show_other_settings(self, item: PixmapNode):
        """顯示其他設定"""
        msg = QMessageBox(self)
        msg.setWindowTitle("其他設定")
        msg.setText("沒有功能owo")
        msg.exec_()

    def clear_canvas(self):
        """清空整個畫布，包括所有圖片和連線"""
        # 顯示警告對話框
        msgBox = QMessageBox()
        msgBox.setWindowTitle("警告")
        msgBox.setText("確定要清空整個畫布嗎？")
        msgBox.setInformativeText("這將刪除所有圖片和連線關係，此操作無法復原。")
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        
        # 如果使用者確認要清空
        if msgBox.exec_() == QMessageBox.Yes:
            # 清空場景
            self.graphics_scene.clear()
            # 清空列表
            self.list_widget.clear()
            self.update_status("已清空畫布")

    def delete_image(self, item: PixmapNode):
        """刪除圖片及其相關連線"""
        if not item:
            return
        
        try:
            # 1. 刪除所有相關的連線
            connections_to_remove = item.connections.copy()  # 創建副本以避免在迭代時修改
            for other_node, line, arrow, _, _ in connections_to_remove:
                if line and line in self.graphics_scene.items():
                    self.graphics_scene.removeItem(line)
                    line = None
                    
                if arrow and arrow in self.graphics_scene.items():
                    self.graphics_scene.removeItem(arrow)
                    arrow = None
                
                # 從另一個節點的 connections 中移除這個連線
                if other_node:
                    other_connections = []
                    for conn in other_node.connections:
                        if conn[0] != item:  # 如果不是要刪除的項目，則保留
                            other_connections.append(conn)
                    other_node.connections = other_connections
            
            # 清空當前節點的連線列表
            item.connections.clear()
            
            # 2. 從列表中移除檔案名稱
            file_name = os.path.basename(item.file_path)
            items = self.list_widget.findItems(file_name, Qt.MatchExactly)
            for list_item in items:
                self.list_widget.takeItem(self.list_widget.row(list_item))
            
            # 3. 從場景中移除圖片節點
            if item in self.graphics_scene.items():
                self.graphics_scene.removeItem(item)
                item = None
            
            self.update_status(f"已刪除圖片: {file_name}")
            self.graphics_scene.update()
            
        except Exception as e:
            if self.log_view:
                self.log_view.append_log(f"刪除圖片時發生錯誤：{str(e)}")

    def toggleConnectionMode(self):
        self.is_connection_mode = not self.is_connection_mode
        if self.is_connection_mode:
            self.update_status("連線模式：點選圖片並拖曳到另一張圖片，以建立連線")
            for item in self.graphics_scene.items():
                if isinstance(item, PixmapNode):
                    item.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
        else:
            self.update_status("一般模式：拖曳圖片或場景")
            for item in self.graphics_scene.items():
                if isinstance(item, PixmapNode):
                    item.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

    def eventFilter(self, watched, event):
        if watched == self.graphics_view.viewport() and isinstance(event, QMouseEvent):
            scene_pos = self.graphics_view.mapToScene(event.pos())

            # 僅在連線模式下處理
            if self.is_connection_mode:
                if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                    item = self.graphics_scene.itemAt(scene_pos, self.graphics_view.transform())
                    if isinstance(item, PixmapNode):
                        # 記錄起始物件與使用者點擊的位置 (local offset)
                        self.start_item = item
                        self.start_offset = item.mapFromScene(scene_pos)
                        self.is_connecting = True

                        # 建立暫時線
                        self.temp_line = QGraphicsLineItem()
                        pen = QPen(Qt.white)
                        pen.setStyle(Qt.DashLine)
                        pen.setWidth(4)
                        pen.setCosmetic(False)
                        self.temp_line.setPen(pen)
                        self.graphics_scene.addItem(self.temp_line)

                        start_scene_pt = item.mapToScene(self.start_offset)
                        self.temp_line.setLine(
                            start_scene_pt.x(),
                            start_scene_pt.y(),
                            scene_pos.x(),
                            scene_pos.y()
                        )

                elif event.type() == QEvent.MouseMove and self.is_connecting and self.temp_line and self.start_item:
                    start_scene_pt = self.start_item.mapToScene(self.start_offset)
                    self.temp_line.setLine(
                        start_scene_pt.x(),
                        start_scene_pt.y(),
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
                            end_offset = end_item.mapFromScene(scene_pos)
                            self.connectTwoItems(self.start_item, self.start_offset, end_item, end_offset)
                            self.update_status("已建立連線")
                        else:
                            self.update_status("取消連線")

                    self.start_item = None
                    self.is_connecting = False

        return super().eventFilter(watched, event)

    def connectTwoItems(self, itemA: PixmapNode, offsetA: QPointF,
                        itemB: PixmapNode, offsetB: QPointF):
        """
        建立「A -> B」的實線與箭頭，並記錄端點對應的 local offset。
        箭頭方向固定從 A 指向 B。
        """
        # 計算 A / B 對應點的世界座標，用來畫線
        a_in_scene = itemA.mapToScene(offsetA)
        b_in_scene = itemB.mapToScene(offsetB)

        # 畫實線
        line = QGraphicsLineItem()
        line.setZValue(-1)
        pen = QPen(Qt.white)
        pen.setWidth(4)
        pen.setCosmetic(False)  # 關鍵：確保線條非 cosmetic，會跟隨縮放
        line.setPen(pen)
        line.setLine(a_in_scene.x(), a_in_scene.y(),
                     b_in_scene.x(), b_in_scene.y())
        self.graphics_scene.addItem(line)

        # 建立箭頭
        arrow = ArrowItem()
        arrow.setZValue(0)  # 顯示在線條之上
        # 不設定忽略變形 (ItemIgnoresTransformations=False)，讓箭頭也可以跟隨縮放
        self.graphics_scene.addItem(arrow)

        # 箭頭位置與角度：固定從 A 指向 B
        mid_x = (a_in_scene.x() + b_in_scene.x()) / 2
        mid_y = (a_in_scene.y() + b_in_scene.y()) / 2
        arrow.setPos(mid_x, mid_y)
        
        # 計算從 A 到 B 的方向
        dx = b_in_scene.x() - a_in_scene.x()
        dy = b_in_scene.y() - a_in_scene.y()
        angle_deg = math.degrees(math.atan2(dy, dx))
        arrow.setRotation(angle_deg)

        # 只在 A 的 connections 中記錄這是「指向 B」的連線
        itemA.connections.append((itemB, line, arrow, offsetA, offsetB))
        # B 的 connections 中不記錄箭頭方向資訊
        itemB.connections.append((itemA, line, None, offsetB, offsetA))

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
        """改進的圖片處理函式"""
        try:
            detect_folder = get_resource_path('detect')
            if not os.path.exists(detect_folder):
                try:
                    os.makedirs(detect_folder)
                except Exception as e:
                    self.label.setText("建立資料夾失敗")
                    if self.log_view:
                        self.log_view.append_log(f"無法建立 detect 資料夾: {str(e)}")
                    return

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(detect_folder, file_name)
            
            # 如果是新檔案才複製
            if not os.path.exists(destination_path):
                try:
                    # 使用 win32file 或基本的檔案操作來複製
                    with open(file_path, 'rb') as src_file:
                        content = src_file.read()
                        with open(destination_path, 'wb') as dst_file:
                            dst_file.write(content)
                except Exception as e:
                    self.label.setText("複製失敗")
                    if self.log_view:
                        self.log_view.append_log(f"複製檔案失敗 ({file_path} -> {destination_path}): {str(e)}")
                        self.log_view.append_log(f"來源檔案存在: {os.path.exists(file_path)}")
                        self.log_view.append_log(f"目標資料夾存在: {os.path.exists(detect_folder)}")
                        self.log_view.append_log(f"目標資料夾權限: {oct(os.stat(detect_folder).st_mode)[-3:]}")
                    return

            try:
                pixmap = QPixmap(destination_path)
                if pixmap.isNull():
                    self.label.setText("載入失敗")
                    if self.log_view:
                        self.log_view.append_log(f"無法載入圖片: {destination_path}")
                    return

                # 建立 PixmapNode 時傳入檔案路徑
                pixmap_node = PixmapNode(pixmap, destination_path)
                pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsMovable, not self.is_connection_mode)
                pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
                self.graphics_scene.addItem(pixmap_node)

                # 檢查列表中是否已有此檔名，沒有才添加
                items = self.list_widget.findItems(file_name, Qt.MatchExactly)
                if not items:
                    self.list_widget.addItem(file_name)
                    # 同步到主視圖的列表
                    if hasattr(self.parent(), 'image_list_widget'):
                        items = self.parent().image_list_widget.findItems(file_name, Qt.MatchExactly)
                        if not items:
                            self.parent().image_list_widget.addItem(file_name)

                self.label.setText("已載入")
                if self.log_view:
                    self.log_view.append_log(f"已載入圖片: {file_name}")

            except Exception as e:
                self.label.setText("處理失敗")
                if self.log_view:
                    self.log_view.append_log(f"處理圖片時發生錯誤: {str(e)}")

        except Exception as e:
            self.label.setText("處理失敗")
            if self.log_view:
                self.log_view.append_log(f"整體處理過程發生錯誤: {str(e)}")

    def wheelEvent(self, event: QWheelEvent):
        """使用滾輪放大縮小，因 pen.setCosmetic(False)，線條與箭頭會跟隨縮放。"""
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.graphics_view.scale(factor, factor)

    def delete_selected_images(self, items):
        """刪除多個選中的圖片"""
        for item in items:
            self.delete_image(item)

    def sync_from_main_view(self, file_name, file_path):
        """從主視圖同步圖片到流程視圖"""
        # 檢查列表中是否已有此檔名
        items = self.list_widget.findItems(file_name, Qt.MatchExactly)
        if not items:
            # 添加到列表
            self.list_widget.addItem(file_name)
            
            # 載入圖片到場景
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap_node = PixmapNode(pixmap, file_path)
                pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsMovable, not self.is_connection_mode)
                pixmap_node.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
                self.graphics_scene.addItem(pixmap_node)

    def save_connections(self):
        """保存所有圖片的連線關係和位置到 JSON 檔案"""
        base_path = get_resource_path('SaveData')
        json_path = os.path.join(base_path, 'connections.json')
        
        # 檢查是否已有存檔
        if os.path.exists(json_path) and os.path.getsize(json_path) > 2:  # 檢查檔案是否大於空的 JSON {}
            # 詢問使用者要新建還是覆蓋
            msgBox = QMessageBox()
            msgBox.setWindowTitle("保存專案")
            msgBox.setText("已存在專案存檔")
            msgBox.setInformativeText("要建立新專案還是覆蓋現有專案？")
            newButton = msgBox.addButton("建立新專案", QMessageBox.ActionRole)
            overwriteButton = msgBox.addButton("覆蓋現有專案", QMessageBox.ActionRole)
            cancelButton = msgBox.addButton("取消", QMessageBox.RejectRole)
            
            msgBox.exec_()
            clicked_button = msgBox.clickedButton()
            
            if clicked_button == cancelButton:
                return
            elif clicked_button == newButton:
                # 讓使用者輸入新檔名
                file_name, ok = QInputDialog.getText(
                    self,
                    "新增專案",
                    "請輸入專案名稱（不需要加副檔名）：",
                    QLineEdit.Normal,
                    ""
                )
                
                if ok and file_name:
                    # 使用使用者輸入的檔名
                    json_path = os.path.join(base_path, f'{file_name}.json')
                elif ok:  # 使用者沒有輸入檔名但按了確定
                    # 找出現有的存檔檔案
                    existing_files = [f for f in os.listdir(base_path) 
                                    if f.startswith('connections_save') and f.endswith('.json')]
                    # 取得最新的編號
                    max_num = 0
                    for f in existing_files:
                        try:
                            num = int(f.replace('connections_save', '').replace('.json', ''))
                            max_num = max(max_num, num)
                        except ValueError:
                            continue
                    # 使用預設檔名
                    json_path = os.path.join(base_path, f'connections_save{max_num + 1}.json')
                else:  # 使用者取消
                    return
            
            elif clicked_button == overwriteButton:
                # 找出所有存檔檔案
                save_files = [f for f in os.listdir(base_path) 
                             if f.endswith('.json')]
                
                if not save_files:
                    self.label.setText("沒有找到任何可覆蓋的存檔")
                    return
                
                # 讓使用者選擇要覆蓋哪個檔案
                item, ok = QInputDialog.getItem(
                    self,
                    "選擇要覆蓋的檔案",
                    "請選擇要覆蓋的存檔：",
                    save_files,
                    0,
                    False
                )
                if not ok:
                    return
                json_path = os.path.join(base_path, item)
        
        # 準備存檔資料
        connections_data = {}
        for item in self.graphics_scene.items():
            if isinstance(item, PixmapNode):
                # 獲取當前節點的檔名和位置
                source_file = os.path.basename(item.file_path)
                pos = item.pos()
                node_data = {
                    'position': {'x': pos.x(), 'y': pos.y()},
                    'connections': []
                }
                
                # 遍歷該節點的所有連線
                for target_node, _, arrow, _, _ in item.connections:
                    target_file = os.path.basename(target_node.file_path)
                    # 只記錄有箭頭的連線（即我是起點的連線）
                    if arrow:
                        node_data['connections'].append({
                            'from': target_file,  # 交換 from 和 to
                            'to': source_file
                        })
                
                connections_data[source_file] = node_data

        # 保存到 JSON 檔案
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(connections_data, f, ensure_ascii=False, indent=4)
        
        self.update_status(f"已保存連線關係和位置到: {os.path.basename(json_path)}")
        
        # 儲存完連線後，分析並儲存步驟順序，傳入實際使用的 json_path
        self.analyze_and_save_steps(json_path)

    def load_connections(self):
        """從 JSON 檔案載入連線關係和圖片位置"""
        base_path = get_resource_path('SaveData')
        
        # 找出所有存檔檔案
        save_files = [f for f in os.listdir(base_path) 
                      if f.endswith('.json')]
        
        if not save_files:
            self.label.setText("沒有找到任何存檔")
            return
        
        # 如果有多個存檔，讓使用者選擇
        if len(save_files) > 1:
            item, ok = QInputDialog.getItem(
                self,
                "選擇存檔",
                "請選擇要載入的存檔：",
                save_files,
                0,
                False
            )
            if not ok:
                return
            json_path = os.path.join(base_path, item)
        else:
            json_path = os.path.join(base_path, save_files[0])
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                connections_data = json.load(f)
            
            # 先清空場景
            self.graphics_scene.clear()
            
            # 建立所有節點
            node_map = {}
            detect_folder = get_resource_path('detect')
            
            # 第一步：建立所有節點
            for file_name, data in connections_data.items():
                if file_name != 'steps':  # 跳過 steps 欄位
                    file_path = os.path.join(detect_folder, file_name)
                    if os.path.exists(file_path):
                        # 創建新的 PixmapNode
                        pixmap = QPixmap(file_path)
                        if not pixmap.isNull():
                            node = PixmapNode(pixmap, file_path)
                            node.setFlag(QGraphicsPixmapItem.ItemIsMovable, not self.is_connection_mode)
                            node.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
                            self.graphics_scene.addItem(node)
                            
                            # 設置位置
                            if 'position' in data:
                                pos = data['position']
                                node.setPos(pos['x'], pos['y'])
                            
                            # 從 steps 中載入所有設定
                            if 'steps' in connections_data:
                                for step_data in connections_data['steps'].values():
                                    if isinstance(step_data, dict):
                                        if step_data.get('location', '').endswith(file_name):
                                            # 載入所有點擊相關設定
                                            node.timeout = step_data.get('timeout', 30)
                                            node.repeat_clicks = step_data.get('repeat_clicks', 1)
                                            node.click_interval = step_data.get('click_interval', 1)
                                            break
                                    elif isinstance(step_data, str) and step_data.endswith(file_name):
                                        # 處理舊格式
                                        node.timeout = 30
                                        node.repeat_clicks = 1
                                        node.click_interval = 1
                        
                            node_map[file_name] = node
                            
                            # 確保列表中有此圖片
                            items = self.list_widget.findItems(file_name, Qt.MatchExactly)
                            if not items:
                                self.list_widget.addItem(file_name)
            
            # 第二步：建立連線
            for file_name, data in connections_data.items():
                if file_name != 'steps' and file_name in node_map:  # 跳過 steps 欄位
                    for conn in data.get('connections', []):
                        from_file = conn['from']
                        to_file = conn['to']
                        
                        # 交換連線方向：from 變成 to，to 變成 from
                        if from_file in node_map and to_file in node_map:
                            from_node = node_map[to_file]  # 注意這裡交換了
                            to_node = node_map[from_file]  # 注意這裡交換了
                            
                            # 建立連線
                            self.connectTwoItems(
                                from_node,
                                QPointF(from_node.boundingRect().center()),
                                to_node,
                                QPointF(to_node.boundingRect().center())
                            )
            
            self.label.setText(f"已載入連線關係和位置: {os.path.basename(json_path)}")
            
        except Exception as e:
            self.label.setText(f"載入連線關係時發生錯誤: {str(e)}")
            if self.log_view:
                self.log_view.append_log(f"載入錯誤詳情: {str(e)}")

    def reload_connections(self):
        """重新載入連線關係"""
        # 只清空場景中的連線，不清空檔案
        # 收集所有需要移除的連線
        lines_and_arrows = set()
        
        # 遍歷所有節點
        for item in self.graphics_scene.items():
            if isinstance(item, PixmapNode):
                # 收集該節點的所有線條和箭頭
                for _, line, arrow, _, _ in item.connections:
                    lines_and_arrows.add(line)
                    lines_and_arrows.add(arrow)
                # 清空該節點的連線列表
                item.connections.clear()
        
        # 從場景中移除所有線條和箭頭
        for item in lines_and_arrows:
            self.graphics_scene.removeItem(item)
        
        # 重新載入連線
        self.load_connections()

    def clear_connections(self):
        """清空所有連線關係"""
        # 收集所有需要移除的連線
        lines_and_arrows = set()
        
        # 遍歷所有節點
        for item in self.graphics_scene.items():
            if isinstance(item, PixmapNode):
                # 收集該節點的所有線條和箭頭
                for _, line, arrow, _, _ in item.connections:
                    lines_and_arrows.add(line)
                    lines_and_arrows.add(arrow)
                # 清空該節點的連線列表
                item.connections.clear()
        
        # 從場景中移除所有線條和箭頭
        for item in lines_and_arrows:
            self.graphics_scene.removeItem(item)
        self.label.setText("已清空所有連線關係")

    def analyze_and_save_steps(self, json_path):
        """分析連線關係並儲存步驟順序"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 建立圖形關係字典 - 修正連線方向
            graph = {}
            for node_name, node_data in data.items():
                if node_name != 'steps':  # 跳過 steps 欄位
                    graph[node_name] = []
                    for conn in node_data.get('connections', []):
                        # 修正：to 是箭頭的起點，from 是終點
                        graph[conn['to']] = graph.get(conn['to'], [])
                        graph[conn['to']].append(conn['from'])
            
            # 找出起點（沒有被指向的節點）
            all_nodes = set(graph.keys())
            destination_nodes = set()
            for connections in graph.values():
                destination_nodes.update(connections)
            start_nodes = all_nodes - destination_nodes
            
            # 從起點開始進行深度優先搜索
            def dfs(node, visited, path):
                if node in path:  # 檢測循環
                    return None
                path.append(node)
                if not graph.get(node, []):  # 如果是終點
                    return path
                for next_node in graph.get(node, []):
                    result = dfs(next_node, visited, path.copy())
                    if result:
                        return result
                return None
            
            # 尋找完整路徑
            complete_path = None
            for start in start_nodes:
                path = dfs(start, set(), [])
                if path:
                    complete_path = path
                    break
            
            if complete_path:
                # 將步驟資訊加入到 JSON 中，使用新的格式包含 timeout, repeat_clicks, click_interval
                steps = {}
                for i, node in enumerate(complete_path):
                    # 使用 get_resource_path 取得相對於資源目錄的路徑
                    relative_path = os.path.join('detect', node)  # 先組合路徑
                    
                    # 使用新的格式，包含 location, timeout, repeat_clicks, click_interval
                    steps[f"Step{i+1}"] = {
                        "location": relative_path,
                        "timeout": 30,  # 預設 timeout 為 30 秒
                        "repeat_clicks": 1,  # 預設點擊次數為 1
                        "click_interval": 1.0  # 預設點擊間隔為 1 秒
                    }
                
                data['steps'] = steps
                
                # 儲存更新後的 JSON
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                self.update_status(f"已分析並儲存步驟順序：{' -> '.join(complete_path)}")
            else:
                self.update_status("無法找到完整的連線路徑")
            
        except Exception as e:
            self.update_status(f"分析步驟時發生錯誤：{str(e)}")

    def update_status(self, message):
        """更新狀態訊息"""
        self.label.setText("已更新")  # 簡短狀態
        if self.log_view:  # 檢查 log_view 是否存在
            self.log_view.append_log(message)  # 詳細訊息寫入 log

    def update_json_timeout(self, item):
        """更新 JSON 中的超時設定"""
        try:
            save_data_path = get_resource_path('SaveData')
            json_files = [f for f in os.listdir(save_data_path) if f.endswith('.json')]
            
            if not json_files:
                if self.log_view:
                    self.log_view.append_log("找不到任何 JSON 檔案")
                return
            
            # 如果有多個檔案，讓使用者選擇
            if len(json_files) > 1:
                file_name, ok = QInputDialog.getItem(
                    self,
                    "選擇檔案",
                    "請選擇要更新的檔案：",
                    json_files,
                    0,
                    False
                )
                if not ok:
                    return
            else:
                file_name = json_files[0]
            
            json_path = os.path.join(save_data_path, file_name)
            
            # 讀取 JSON 檔案
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 取得目標檔案名稱
            target_file = os.path.basename(item.file_path)
            
            # 在 steps 中找到對應的步驟並更新設定
            if 'steps' in data:
                updated = False
                for step_data in data['steps'].values():
                    if isinstance(step_data, dict):
                        if step_data.get('location', '').endswith(target_file):
                            step_data['timeout'] = item.timeout
                            updated = True
                    elif isinstance(step_data, str) and step_data.endswith(target_file):
                        # 如果是舊格式，轉換為新格式
                        step_data = {
                            'location': step_data,
                            'timeout': item.timeout
                        }
                        updated = True
                
                if updated:
                    # 保存更新後的 JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    if self.log_view:
                        self.log_view.append_log(f"已更新節點 {target_file} 的超時設定")
                else:
                    if self.log_view:
                        self.log_view.append_log(f"在 JSON 中找不到對應的節點：{target_file}")
            
        except Exception as e:
            if self.log_view:
                self.log_view.append_log(f"更新超時設定時發生錯誤：{str(e)}")

    def load_connections_from_json(self, json_path):
        """從 JSON 檔案載入連線關係"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 首先載入所有節點的位置和設定
            for file_name, node_data in data.items():
                if file_name != "steps":  # 跳過 steps 部分
                    # 尋找對應的 PixmapNode
                    for item in self.graphics_scene.items():
                        if isinstance(item, PixmapNode) and os.path.basename(item.file_path) == file_name:
                            # 設置位置
                            if "position" in node_data:
                                item.setPos(node_data["position"]["x"], node_data["position"]["y"])
                            
                            # 從 steps 中找到對應的設定並同步到節點
                            if "steps" in data:
                                for step in data["steps"].values():
                                    if isinstance(step, dict) and step.get("location", "").endswith(file_name):
                                        # 同步點擊設定
                                        item.timeout = step.get("timeout", 30)
                                        item.repeat_clicks = step.get("repeat_clicks", 1)
                                        item.click_interval = step.get("click_interval", 0.5)
                                        break
            
            # 然後建立連線關係
            for file_name, node_data in data.items():
                if file_name != "steps" and "connections" in node_data:
                    source_item = None
                    # 找到源節點
                    for item in self.graphics_scene.items():
                        if isinstance(item, PixmapNode) and os.path.basename(item.file_path) == file_name:
                            source_item = item
                            break
                    
                    if source_item:
                        # 建立所有連線
                        for conn in node_data["connections"]:
                            target_file = conn["from"]  # 注意：JSON 中的 from 是目標節點
                            # 找到目標節點
                            for item in self.graphics_scene.items():
                                if isinstance(item, PixmapNode) and os.path.basename(item.file_path) == target_file:
                                    # 建立連線（使用預設的偏移量）
                                    self.connectTwoItems(source_item, QPointF(0, 0), item, QPointF(0, 0))
                                    break
            
            if self.log_view:
                self.log_view.append_log("已從 JSON 載入連線關係")
            
        except Exception as e:
            if self.log_view:
                self.log_view.append_log(f"載入連線關係時發生錯誤：{str(e)}")

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
