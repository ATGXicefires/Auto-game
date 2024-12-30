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

class ButtonPropertyManager:
    def __init__(self, default_properties=None):
        """
        初始化 ButtonPropertyManager。
        :param default_properties: 默認屬性（字典形式）
        """
        self.default_properties = default_properties or {}

    def apply_properties(self, buttons, properties_list):
        """
        批量为多个按钮设置属性。
        :param buttons: QPushButton 对象列表。
        :param properties_list: 属性字典列表，每个字典对应一个按钮。
        """
        if len(buttons) != len(properties_list):
            raise ValueError("The number of buttons and properties must match.")

        for button, properties in zip(buttons, properties_list):
            merged_properties = self.merge_properties(properties)
            self.apply_properties_to_button(button, merged_properties)

    def apply_properties_to_button(self, button, properties):
        """
        为单个按钮设置属性。
        :param button: QPushButton 对象
        :param properties: 属性字典
        """
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary.")

        for attr, value in properties.items():
            if hasattr(button, attr):
                try:
                    setattr(button, attr, value)
                except Exception as e:
                    self.handle_property_error(button, attr, value, e)
            else:
                self.handle_missing_attribute(button, attr)

    def merge_properties(self, properties):
        """
        合并默认属性和指定属性。
        :param properties: 指定的属性字典
        :return: 合并后的字典
        """
        return {**self.default_properties, **properties}

    def handle_property_error(self, button, attr, value, exception):
        """
        屬性設置失敗時的錯誤處理。
        """
        print(f"Error setting attribute '{attr}' to '{value}' on button '{button.text()}': {exception}")

    def handle_missing_attribute(self, button, attr):
        """
        處理缺少屬性的情況。
        """
        print(f"Button '{button.text()}' does not have attribute '{attr}'.")
