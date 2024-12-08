from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QPlainTextEdit, QFileDialog

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
