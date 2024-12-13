import sys
from PySide6.QtWidgets import QApplication
from ui_components import MainWindow
from functions import ensure_cache_directory, ensure_sv_json, ensure_detect_directory

if __name__ == "__main__":
    # 確保 cache & detect 資料夾存在
    ensure_cache_directory()
    ensure_detect_directory()
    # 確保 sv.json 文件存在
    ensure_sv_json()
    
    # 創建 QApplication 實例
    app = QApplication(sys.argv)
    # 創建 MainWindow 的實例
    main_window = MainWindow()
    # 顯示主窗口
    main_window.show()
    # 連接信號到槽函數
    main_window.start_signal.connect(main_window.on_start_button_click)
    # 在主執行緒中運行應用程式
    sys.exit(app.exec()) 