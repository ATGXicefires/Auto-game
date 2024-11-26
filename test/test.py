from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
import sys
import os
import shutil
from ui_test import Ui_MainWindow  # 引入生成的 UI 類

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # 設置 UI

        # 連接按鈕的點擊事件
        self.ui.pushButton1.clicked.connect(lambda: self.openFileDialog(1))
        self.ui.pushButton2.clicked.connect(lambda: self.openFileDialog(2))
        self.ui.pushButton3.clicked.connect(lambda: self.openFileDialog(3))
        self.ui.pushButton4.clicked.connect(lambda: self.openFileDialog(4))
        self.ui.pushButton5.clicked.connect(lambda: self.openFileDialog(5))

    def openFileDialog(self, buttonNumber):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "選擇文件", "", "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)  # 打印文件路徑

            # 記錄文件位置
            self.selectedFilePath = fileName

            # 構建目標目錄和文件名
            targetDir = os.path.join(os.getcwd(), "test", "cache")
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)

            newFileName = f"{buttonNumber}"  # 根據按鈕編號命名文件
            newFilePath = os.path.join(targetDir, newFileName)

            try:
                # 複製文件並重新命名
                shutil.copy(fileName, newFilePath)
                print(f"文件已複製並重新命名為: {newFilePath}")
            except Exception as e:
                print(f"文件複製失敗: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())