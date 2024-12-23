import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPalette, QColor, Qt
from main_view import MainWindow
from functions import ensure_cache_directory, ensure_sv_json, ensure_detect_directory, clear_sv_json, Click_step_by_step, ADB_Click_step_by_step, initialize_setting_file, initialize_connections_file, ensure_save_data_directory

class Worker(QThread):
    finished = Signal()
    log_signal = Signal(str)
    
    def __init__(self, step_array, log_view, is_adb_mode):
        super().__init__()
        self.step_array = step_array
        self.log_view = log_view
        self.is_adb_mode = is_adb_mode

    def run(self):
        # 根據模式選擇不同的點擊函數
        if self.is_adb_mode:
            ADB_Click_step_by_step(self.step_array, self.log_view)
        else:
            Click_step_by_step(self.step_array, self.log_view)
        self.finished.emit()

if __name__ == "__main__":
    ensure_cache_directory()
    ensure_detect_directory()
    ensure_save_data_directory()
    initialize_setting_file()
    initialize_connections_file()
    ensure_sv_json()
    clear_sv_json()
    # 創建 QApplication 實例
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
            font-size: 16px;
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
        QMenu {
            background-color: #353535;
            border: 1px solid #3d3d3d;
        }
        QMenu::item {
            padding: 5px 20px;
        }
        QMenu::item:selected {
            background-color: #2a82da;
        }
        /* 為特定的選單項目設定顏色 */
        QMenu::item[class="danger"] {
            color: #ff4444;
        }
    """)

    # 創建 MainWindow 的實例
    main_window = MainWindow()
    # 顯示主窗口
    main_window.show()
    # 創建 Worker 執行緒
    worker = Worker(main_window.step_array, main_window.log_view, main_window.is_adb_mode)
    # 連接 Worker 的 finished 信號到主窗口的槽函數
    worker.finished.connect(lambda: main_window.log_view.append_log("點擊操作完成"))
    # 連接主窗口的 start_signal 到 Worker 的 start 方法
    main_window.start_signal.connect(worker.start)
    # 在主執行緒中運行應用程式
    sys.exit(app.exec()) 