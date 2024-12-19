import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal
from main_view import MainWindow
from functions import ensure_cache_directory, ensure_sv_json, ensure_detect_directory, clear_sv_json, Click_step_by_step, ADB_Click_step_by_step

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
    # 創建 Worker 執行緒
    worker = Worker(main_window.step_array, main_window.log_view, main_window.is_adb_mode)
    # 連接 Worker 的 finished 信號到主窗口的槽函數
    worker.finished.connect(lambda: main_window.log_view.append_log("點擊操作完成"))
    # 連接主窗口的 start_signal 到 Worker 的 start 方法
    main_window.start_signal.connect(worker.start)
    # 在主執行緒中運行應用程式
    sys.exit(app.exec()) 