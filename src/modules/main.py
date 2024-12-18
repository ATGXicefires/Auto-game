import sys
from PySide6.QtWidgets import QApplication
from main_view import MainWindow
from functions import ensure_cache_directory, ensure_sv_json, ensure_detect_directory,clear_sv_json
from PySide6.QtCore import QThread, Signal

class WorkerThread(QThread):
    # 定義信號
    start_signal = Signal()

    def run(self):
        # 在這裡執行執行緒的工作
        # 當需要時發送信號
        self.start_signal.emit()

if __name__ == "__main__":

    # 確保 cache 目錄存在
    ensure_cache_directory()
    ensure_detect_directory()
    # 確保 sv.json 文件存在
    ensure_sv_json()
    # 清空 sv.json 文件
    clear_sv_json()
    # 創建 QApplication 實例
    app = QApplication(sys.argv)
    # 創建 MainWindow 的實例
    main_window = MainWindow()
    # 顯示主窗口
    main_window.show()
    # 創建 WorkerThread 的實例
    worker_thread = WorkerThread()

    # 連接信號到槽函數
    worker_thread.start_signal.connect(main_window.on_start_button_click)

    # 啟動執行緒
    worker_thread.start()

    # 在主執行緒中運行應用程式
    sys.exit(app.exec()) 