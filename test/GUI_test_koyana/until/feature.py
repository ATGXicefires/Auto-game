from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QPushButton,
                               QWidget, QVBoxLayout)

class file_operations:
    def open_file_dialog(parent=None, caption="选择文件", filter="All Files (*.*)"):
        """
        打开文件选择对话框。

        :param parent: 父窗口（可以是 QWidget 或 None）
        :param caption: 对话框标题
        :param filter: 文件类型过滤器
        :return: 选择的文件路径（str），如果取消选择则返回空字符串
        """
        file_path, _ = QFileDialog.getOpenFileName(parent, caption, filter)
        return file_path

    def save_file_dialog(parent=None, caption="保存文件", filter="All Files (*.*)"):
        file_path, _ = QFileDialog.getSaveFileName(parent, caption, filter)
        return file_path

    def create_button(buttons):
        """生成按钮"""
        button_list = []
        for button_text, callback in buttons:
            button = QPushButton(button_text)
            button.clicked.connect(callback)
            button_list.append(button)
        return button_list

    def create_widget_with_custom_layout(elements, layout):
        """
        创建一个带有自定义布局的 QWidget
        :param elements: 需要添加到布局的元素列表
        :param layout: 自定义布局 (例如 QVBoxLayout、QHBoxLayout、QGridLayout)
        :return: 带有布局和元素的 QWidget
        """
        widget = QWidget()
        for element in elements:
            layout.addWidget(element)
        widget.setLayout(layout)
        return widget
