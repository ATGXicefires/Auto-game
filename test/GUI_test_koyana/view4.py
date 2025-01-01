from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QLabel, QScrollArea, QPushButton, QSplitter
from PySide6.QtCore import Signal, Qt
from until.feature import create_button, ButtonPropertyManager

class View4(QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui():
        create_button(["test1",],
                      ["test2",],
                      ["test3",])
