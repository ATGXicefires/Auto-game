from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QCheckBox, QPlainTextEdit, QFileDialog, QComboBox, QSlider, QLabel
)
from PySide6.QtCore import Qt


class View1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        # 左側的Checkbox和按鈕
        left_layout = QVBoxLayout()
        self.checkbox1 = QCheckBox("選項 1")
        self.checkbox2 = QCheckBox("選項 2")
        self.checkbox3 = QCheckBox("選項 3")
        self.button = QPushButton("提交")
        left_layout.addWidget(self.checkbox1)
        left_layout.addWidget(self.checkbox2)
        left_layout.addWidget(self.checkbox3)
        left_layout.addWidget(self.button)

        # 右側的文本框
        self.text_edit = QTextEdit()

        layout.addLayout(left_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)


class View2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        self.file_button = QPushButton("選擇文件")
        self.path_display = QPlainTextEdit()
        self.path_display.setReadOnly(True)
        self.file_button.clicked.connect(self.open_file_dialog)

        layout.addWidget(self.file_button)
        layout.addWidget(self.path_display)
        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇文件")
        if file_path:
            self.path_display.setPlainText(file_path)


class View3(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # 模式選擇
        self.combo_box = QComboBox()
        self.combo_box.addItems(["淺色模式", "深色模式"])

        # 滑條調整主題
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.update_theme)

        layout.addWidget(QLabel("選擇模式:"))
        layout.addWidget(self.combo_box)
        layout.addWidget(QLabel("調整主題:"))
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_theme(self):
        value = self.slider.value()
        print(f"滑條值: {value}")  # 這裡可擴展成更新主題


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 多視圖示例")

        self.view1 = View1()
        self.view2 = View2()
        self.view3 = View3()

        self.views = [self.view1, self.view2, self.view3]
        self.current_view = 0

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # 視圖切換按鈕
        self.view1_button = QPushButton("視圖 1")
        self.view2_button = QPushButton("視圖 2")
        self.view3_button = QPushButton("視圖 3")
        self.view1_button.clicked.connect(lambda: self.switch_view(0))
        self.view2_button.clicked.connect(lambda: self.switch_view(1))
        self.view3_button.clicked.connect(lambda: self.switch_view(2))

        self.button_layout.addWidget(self.view1_button)
        self.button_layout.addWidget(self.view2_button)
        self.button_layout.addWidget(self.view3_button)

        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.views[self.current_view])

        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def switch_view(self, index):
        self.main_layout.removeWidget(self.views[self.current_view])
        self.views[self.current_view].hide()
        self.current_view = index
        self.main_layout.addWidget(self.views[self.current_view])
        self.views[self.current_view].show()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
