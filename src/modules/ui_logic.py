import sys
import os
import shutil
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QMenu, QLineEdit, QMessageBox, QGraphicsView, QGraphicsScene, QStyle, QStyleOptionSlider, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QIntValidator, QPainter, QFont, QPen
from PySide6.QtCore import Qt, Signal
from functions import get_resource_path, load_json_variables, get_max_step_value, Click_step_by_step,adb_screenshot
from log_view import LogView

# 在 MainWindow 類別中使用這些邏輯方法
class MainWindow(QMainWindow):
    # ... existing code ...

    def __init__(self):
        super(MainWindow, self).__init__()
        # ... existing code ...

        # 在初始化時讀取模式設置
        self.load_mode_setting()

        # 初始化日誌視圖
        self.log_view = LogView(self)

    def load_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        if os.path.exists(setting_path):
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                mode = settings.get('detect_mode', 'Windows')
                self.mode_button.setChecked(mode == 'ADB')
                self.mode_button.setText(f"模式: {mode}")
        else:
            # 如果文件不存在，默認設置為 Windows 模式
            self.mode_button.setChecked(False)
            self.mode_button.setText("模式: Windows")

    def save_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        mode = "ADB" if self.mode_button.isChecked() else "Windows"
        settings = {'detect_mode': mode}
        with open(setting_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        print(f"模式已保存: {mode}")

    def on_button_click(self):
        handle_file_selection(self)

    def clear_save_data(self):
        clear_save_data(self)

    def clear_json_file(self):
        clear_json_file(self)

    def toggle_mode(self):
        if self.mode_button.isChecked():
            self.mode_button.setText("模式: ADB")
        else:
            self.mode_button.setText("模式: Windows")
        
        # 保存當前模式到 setting.json
        setting_path = get_resource_path('cache/setting.json')
        try:
            # 讀取現有設定
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 只更新 detect_mode，保留其他設定
            settings['detect_mode'] = "ADB" if self.mode_button.isChecked() else "Windows"
            
            # 保存更新後的設定
            with open(setting_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
        except Exception as e:
            self.log_view.append_log(f"保存模式設定時發生錯誤: {str(e)}")

    def toggle_view(self):
        """切換主視圖和日誌視圖"""
        if self.centralWidget() == self.log_view:
            self.setCentralWidget(self.main_widget)  # 切換回主視圖
        else:
            self.setCentralWidget(self.log_view)  # 切換到日誌視圖

    # 其他方法的實現

def clear_json_file(main_window):
    # 清空 JSON 檔案並設置為全空
    json_path = get_resource_path("SaveData/sv.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=4)  # 設置為空字典
    print(f"Cleared {json_path} and set to empty")

def get_resource_path(relative_path):
    """獲取資源文件的正確路徑"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def handle_file_selection(main_window):
    # 打開文件選擇對話框，允許多選
    file_paths, _ = QFileDialog.getOpenFileNames(main_window, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
    
    if file_paths:
        target_dir = get_resource_path("detect")
        os.makedirs(target_dir, exist_ok=True)
        
        json_path = get_resource_path("SaveData/sv.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # 找到目前最大的 Img[X] 的 X 值
        max_index = 0
        for key in data.keys():
            if key.startswith("Img["):
                try:
                    index = int(key[4:-1])
                    if index > max_index:
                        max_index = index
                except ValueError:
                    continue

        # 複製文件到目標資料夾並更新 JSON
        for i, file_path in enumerate(file_paths, start=1):
            target_path = os.path.join(target_dir, os.path.basename(file_path))
            if not os.path.exists(target_path):  # 如果檔案不存在才複製
                shutil.copy(file_path, target_path)
                print(f"Image copied to {target_path}")

            # 將目標路徑轉換為相對路徑
            relative_path = os.path.relpath(target_path, start=os.getcwd())

            # 儲存路徑到 JSON 檔案
            data[f"Img[{max_index + i}]"] = relative_path

            # 在列表中添加新圖片的檔名（如果不存在）
            file_name = os.path.basename(relative_path)
            items = main_window.image_list_widget.findItems(file_name, Qt.MatchExactly)
            if not items:
                main_window.image_list_widget.addItem(file_name)
                # 同步更新 ProcessView 的列表
                main_window.process_view.sync_from_main_view(file_name, target_path)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Paths saved to {json_path}")

def display_image(main_window, item):
    """顯示選中的圖片"""
    image_name = item.text()
    json_path = get_resource_path("SaveData/sv.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找到對應的圖片路徑
    for key, path in data.items():
        if os.path.basename(path) == image_name:
            pixmap = QPixmap(path)
            main_window.graphics_scene.clear()  # 清除現有的場景
            main_window.graphics_scene.addPixmap(pixmap)  # 添加新圖片
            main_window.current_image_key = key  # 更新當前圖片的鍵
            break

def clear_detect(main_window):
    """清理 detect 資料夾中的所有圖片"""
    detect_path = get_resource_path("detect")
    
    # 確認對話框
    reply = QMessageBox.question(
        main_window,
        "確認清理",
        "確定要清理所有已上傳的圖片嗎？\n此操作無法撤銷。",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        try:
            # 清空 detect 資料夾中的所有文件
            for filename in os.listdir(detect_path):
                file_path = os.path.join(detect_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # 清空圖片列表
            main_window.image_list_widget.clear()
            
            # 清空場景
            main_window.graphics_scene.clear()
            
            # 清空 JSON 檔案
            clear_json_file(main_window)
            
            QMessageBox.information(main_window, "完成", "已上傳的圖片已清理完成！")
            print("已上傳的圖片已清理完成")
            
        except Exception as e:
            QMessageBox.warning(main_window, "錯誤", f"清理已上傳的圖片時發生錯誤：{str(e)}")
            print(f"清理已上傳的圖片時發生錯誤：{str(e)}")

def clear_save_data(main_window):
    """清理存檔資料夾內的檔案，但保留資料夾和 sv.json"""
    cache_path = get_resource_path('SaveData')
    if os.path.exists(cache_path):
        # 遍歷資料夾中的所有檔案並刪除，但保留 sv.json
        for filename in os.listdir(cache_path):
            # 跳過 sv.json
            if filename == 'sv.json':
                continue
                
            file_path = os.path.join(cache_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"刪除檔案時發生錯誤: {e}")
                continue
        
        print(f"已清除存檔資料夾內容: {cache_path}")
        main_window.log_view.append_log("已清除存檔資料夾內容")

def process_set_button_click(main_window):
    """切換到流程視圖頁籤"""
    # 找到 process_view 的索引並切換到該頁籤
    process_view_index = main_window.tabs.indexOf(main_window.process_view)
    if process_view_index != -1:  # 確保找到了 process_view
        main_window.tabs.setCurrentIndex(process_view_index)

def on_zoom_slider_change(main_window):
    # 當滑桿值改變時更新圖片顯示
    scale_factor = main_window.zoom_slider.value() / 100.0
    main_window.graphics_view.resetTransform()  # 重置任何現有的變換
    main_window.graphics_view.scale(scale_factor, scale_factor)  # 根據滑桿的值縮放圖片
    main_window.zoom_slider.setToolTip(f"{main_window.zoom_slider.value()}%")  # 更新滑桿的提示文字

def show_context_menu(main_window, position):
    # 創建右鍵菜單
    menu = QMenu()
    delete_action = menu.addAction("刪除圖片")
    action = menu.exec_(main_window.image_list_widget.mapToGlobal(position))
    if action == delete_action:
        delete_selected_image(main_window)

def delete_selected_image(main_window):
    # 刪除選中的圖片
    selected_item = main_window.image_list_widget.currentItem()
    if selected_item:
        image_name = selected_item.text()
        main_window.image_list_widget.takeItem(main_window.image_list_widget.row(selected_item))
        remove_image_from_json_and_disk(main_window, image_name)

def remove_image_from_json_and_disk(main_window, image_name):
    json_path = get_resource_path("SaveData/sv.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 找到並刪除對應的圖片路徑
    key_to_remove = None
    for key, path in data.items():
        if os.path.basename(path) == image_name:
            key_to_remove = key
            break

    if key_to_remove:
        # 刪除 JSON 中的條目
        del data[key_to_remove]

        # 刪除 detect 資料夾中的文件
        file_path = get_resource_path(path)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path} from disk")

        # 更新 JSON 文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Deleted {image_name} from JSON")

def update_json_with_input(main_window):
    # 更新 JSON 文件中的 Step[Y] 值
    if main_window.current_image_key:
        json_path = get_resource_path("SaveData/sv.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 更新對應的 Step[Y] 值
        new_value = main_window.input_box.text()
        if new_value.isdigit():
            new_key = f"Step[{new_value}]"
            if new_key in data:
                QMessageBox.warning(main_window, "重複的數字", f"數字 {new_value} 已被使用，請選擇其他數字。")
            else:
                # 保留 Img[X]，同時新增 Step[Y]
                data[new_key] = data[main_window.current_image_key]
                main_window.current_image_key = new_key  # 更新當前圖片的鍵

                # 寫入更新後的 JSON 文件
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Added new key: {new_key} with value from {main_window.current_image_key}")

def clear_adb_settings(main_window):
    """清除 ADB 設定"""
    setting_path = get_resource_path('cache/setting.json')
    if os.path.exists(setting_path):
        try:
            # 讀取現有設定
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 將 ADB IP 地址設定為空字串
            settings['adb_ip_address'] = ""
                
            # 保存更新後的設定
            with open(setting_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            main_window.log_view.append_log("已清除 ADB IP 設定")
            
        except Exception as e:
            main_window.log_view.append_log(f"清除 ADB 設定時發生錯誤: {str(e)}")


