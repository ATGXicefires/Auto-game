### 這是一個圖像識別自動化工具

### 工具使用方法

1. 下載最新的Release版本
2. 解壓縮檔案
3. 執行.exe檔案
4. 匯入所需檢測的圖片
5. 進入流程編輯頁面設置順序
6. 按下「程式開始」，並選擇想要執行的存檔

### 想變動原代碼的話看這裡

程式語言 : Python(3.10.6)

1. git clone https://github.com/ATGXicefires/Auto-game.git
2. 主要程式的編寫位置在src/modules/
3. 建置完虛擬環境後在終端機輸入pip install -r requirements.txt (請確保自己是使用python 3.10.6
4. 在終端機輸入python src/modules/main.py 即可執行

main.py 是主程式，負責整個程式的運行

main_view.py 是主要視圖，負責視覺化

ui_logic.py 是主視圖的邏輯，負責程式的運行

function.py 是功能函式，負責功能實現

log_view.py 是日誌視圖，負責日誌的顯示

process_view.py 是流程視圖，負責流程的處理和視覺化

clicking_functions.py 是處理ClickWorker2相關的點擊功能實現

### 這是高三專題實作，僅供學術研究使用

編程者 : ATGXicefires & wj6wj6(Koyana) & Creeperlol

### 注意事項

請確保圖片解析度與要偵測的畫面一樣

例如: 偵測1920*1080的畫面，圖片要從1920*1080的畫面擷取
裁切圖片不影響偵測，但縮放圖片會影響偵測
