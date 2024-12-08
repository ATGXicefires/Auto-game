def apply_light_theme():
    """淺色模式樣式"""
    return """
    QWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QPushButton {
        border: 1px solid gray;
        border-radius: 5px;
        background-color: #f0f0f0;
        color: black;
    }
    QPushButton#viewButton {
        border: none;
        background-color: transparent;
        color: black;
        padding: 10px;
    }
    QPushButton#viewButton:checked {
        background-color: black;
        color: white;
        border-bottom: 2px solid blue;
    }
    QFrame {
        background-color: #d0d0d0;
        height: 2px;
        border: none;
    }
    QCheckBox, QLineEdit, QTextEdit, QComboBox {
        border: 1px solid gray;
        border-radius: 5px;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #d0d0d0;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        width: 14px;
        height: 14px;
        margin: -4px 0;
        background: #0078d7;
        border: 1px solid gray;
        border-radius: 7px;
    }
    QSlider::sub-page:horizontal {
        background: #0078d7;
        border-radius: 3px;
    }
    """

def apply_dark_theme():
    """深色模式樣式"""
    return """
    QWidget {
        background-color: #2e2e2e;
        color: #ffffff;
    }
    QPushButton {
        border: 1px solid #5a5a5a;
        border-radius: 5px;
        background-color: #3c3c3c;
        color: white;
    }
    QPushButton#viewButton {
        border: none;
        background-color: transparent;
        color: white;
        padding: 10px;
    }
    QPushButton#viewButton:checked {
        background-color: transparent;
        color: blue;
        border-bottom: 2px solid blue;
    }
    QFrame {
        background-color: #3a3a3a;
        height: 2px;
        border: none;
    }
    QCheckBox, QLineEdit, QTextEdit, QComboBox {
        border: 1px solid #5a5a5a;
        border-radius: 5px;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #4a4a4a;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        width: 14px;
        height: 14px;
        margin: -4px 0;
        background: #1a73e8;
        border: 1px solid #5a5a5a;
        border-radius: 7px;
    }
    QSlider::sub-page:horizontal {
        background: #1a73e8;
        border-radius: 3px;
    }
    """
