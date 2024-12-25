from PySide6.QtWidgets import QFileDialog

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
