def button_active_style():
    """當前視圖按鈕的樣式"""
    return """
    QPushButton {
        color: white; /* 深色模式下字體顯示為白色 */
        border: none;
        border-bottom: 2px solid blue;
        font-weight: bold;
        background-color: transparent;
        padding: 10px;
    }
    """

def button_inactive_style():
    """非當前視圖按鈕的樣式"""
    return """
    QPushButton {
        color: gray; /* 非激活按鈕使用灰色字體 */
        border: none;
        background-color: transparent;
        padding: 10px;
    }
    """

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
    }
    QLineEdit, QTextEdit {
        border: 1px solid gray;
        border-radius: 5px;
    }
    QComboBox {
        border: 1px solid gray;
        border-radius: 5px;
    }
    QSlider::groove:horizontal {
        border: 1px solid gray;
        height: 6px;
        background: #e0e0e0;
    }
    QSlider::handle:horizontal {
        background: #0078d7;
        border: 1px solid gray;
        width: 12px;
        margin: -5px 0;
        border-radius: 4px;
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
    }
    QLineEdit, QTextEdit {
        border: 1px solid #5a5a5a;
        border-radius: 5px;
    }
    QComboBox {
        border: 1px solid #5a5a5a;
        border-radius: 5px;
    }
    QSlider::groove:horizontal {
        border: 1px solid #5a5a5a;
        height: 6px;
        background: #4a4a4a;
    }
    QSlider::handle:horizontal {
        background: #1a73e8;
        border: 1px solid #5a5a5a;
        width: 12px;
        margin: -5px 0;
        border-radius: 4px;
    }
    """