from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIntValidator
from ui_components import MainWindow
from ui_logic import clear_json_file, handle_file_selection
from functions import get_resource_path, load_json_variables, get_max_step_value, Click_step_by_step

# 在 MainWindow 類別中使用這些邏輯方法
class MainWindow(QMainWindow):
    # ... existing code ...

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

    # 其他方法的實現