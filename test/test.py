from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
import sys
import os
import shutil

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.resize(1280, 720)  # 設置初始視窗大小為 1280x720

    def setupUi(self, MainWindow):
        self.setWindowTitle("MainWindow")
        self.setGeometry(100, 100, 300, 200)
        
        # 創建按鈕
        self.pushButton = QPushButton("步驟1 圖片選擇", self)
        self.pushButton.setGeometry(100, 50, 100, 100)
        
        # 創建其他按鈕
        self.pushButton2 = QPushButton("步驟2 圖片選擇", self)
        self.pushButton2.setGeometry(220, 50, 100, 100)
        
        self.pushButton3 = QPushButton("步驟3 圖片選擇", self)
        self.pushButton3.setGeometry(340, 50, 100, 100)
        
        # 連接按鈕的點擊事件
        self.pushButton.clicked.connect(lambda: self.openFileDialog(1))
        self.pushButton2.clicked.connect(lambda: self.openFileDialog(2))
        self.pushButton3.clicked.connect(lambda: self.openFileDialog(3))

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