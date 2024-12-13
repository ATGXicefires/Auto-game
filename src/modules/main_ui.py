from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIntValidator
from ui_components import MainWindow
from ui_logic import clear_json_file, handle_file_selection
from functions import get_resource_path, load_json_variables, get_max_step_value, Click_step_by_step
import json
import os

# 在 MainWindow 類別中使用這些邏輯方法
class MainWindow(QMainWindow):
    # ... existing code ...

    def __init__(self):
        super(MainWindow, self).__init__()
        # ... existing code ...

        # 在初始化時讀取模式設置
        self.load_mode_setting()

    def load_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        if os.path.exists(setting_path):
            with open(setting_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                mode = settings.get('detect_mode', 'Windows')
                self.mode_button.setChecked(mode == 'ADB')
                self.mode_button.setText(f"模式: {mode}")
        else:
            # 如果文件不存在，默認設置為 Windows 模式
            self.mode_button.setChecked(False)
            self.mode_button.setText("模式: Windows")

    def save_mode_setting(self):
        setting_path = get_resource_path('cache/setting.json')
        mode = "ADB" if self.mode_button.isChecked() else "Windows"
        settings = {'detect_mode': mode}
        with open(setting_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        print(f"模式已保存: {mode}")

    def on_button_click(self):
        handle_file_selection(self)

    def clear_json_file(self):
        clear_json_file()

    def on_start_button_click(self):
        # 這裡是 Start_ON 的邏輯
        # 獲取當前模式
        is_adb_mode = self.mode_button.isChecked()
        mode_text = "ADB" if is_adb_mode else "Windows"
        print(f"當前模式: {mode_text}")

        # 保存當前模式到 setting.json
        self.save_mode_setting()

        # 使用 get_resource_path 來獲取 sv.json 的正確路徑
        json_path = get_resource_path('test/json_test/sv.json')
        # 導入 sv.json 的變數
        json_variables = load_json_variables(json_path)
        max_step_value = 0
        print("Start")
        
        # 最小化主窗口
        self.showMinimized()
        
        # 找出 "Step[Y]" 的最大 Y 值
        max_step_value = get_max_step_value(json_variables)
        print(f"最大 Step[Y] 值: {max_step_value}")

        # 將 Step[Y] 的內容值存入 step_array
        step_array = []
        for i in range(1, max_step_value + 1):
            step_key = f"Step[{i}]"
            if step_key in json_variables:
                step_array.append(json_variables[step_key])
        
        # 打印出 step_array 中的所有值
        for index in range(max_step_value):
            print(f"step_array[{index}]: {step_array[index]}")

        # 根據模式選擇不同的點擊函數
        if is_adb_mode:
            # TODO: 實現 ADB 模式的點擊函數
            print("ADB 模式尚未實現")
        else:
            # 使用原有的 Windows 模式點擊函數
            Click_step_by_step(step_array)

    def toggle_mode(self):
        if self.mode_button.isChecked():
            self.mode_button.setText("模式: ADB")
        else:
            self.mode_button.setText("模式: Windows")
        # 每次切換模式時保存設置
        self.save_mode_setting()

    # 其他方法的實現