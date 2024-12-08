from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit, QCheckBox

class View1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.checkbox1 = QCheckBox("選項 1")
        self.checkbox2 = QCheckBox("選項 2")
        self.checkbox3 = QCheckBox("選項 3")
        self.button = QPushButton("提交")
        left_layout.addWidget(self.checkbox1)
        left_layout.addWidget(self.checkbox2)
        left_layout.addWidget(self.checkbox3)
        left_layout.addWidget(self.button)

        self.text_edit = QTextEdit()
        layout.addLayout(left_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
