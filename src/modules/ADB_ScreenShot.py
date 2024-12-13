import os

if __name__ == '__main__':
    # 讓程式持續運作
    while True:
        # 透過 adb 去將模擬器截圖起來儲存於 sdcard 當中
        os.system('adb shell /system/bin/screencap -p /sdcard/screencap.png')
        # 透過 adb 將模擬器儲存的截圖輸出到專案根目錄底下
        os.system('adb pull /sdcard/screencap.png ./src/modules/detect/screencap.png')
        break