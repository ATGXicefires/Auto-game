## 這是一個圖像識別自動化工具
![GitHub tag (latest by date)](https://img.shields.io/github/v/release/ATGXicefires/Auto-game)
### 🕹️ 使用方法

1. 下載Release最新版檔案
2. 解壓縮檔案
3. 執行 `AutoGameClicker v0.4.2.exe`
4. 匯入所需檢測的圖片
5. 進入流程編輯頁面設置順序
6. 按下「程式開始」，並選擇想要執行的存檔

### 💻 開發

#### 需求:

```
Python 3.10.6
```

#### 使用方法:
```bash
git clone https://github.com/ATGXicefires/Auto-game.git   # 複製專案
cd Audo-game                                              # 主要程式的編寫位置在 src/modules/
python -m venv venv                                       # 設置虛擬環境
.\testenv\Scripts\activate.ps1                            # 啟用虛擬環境
pip install -r requirements.txt                           # 安裝需求項 (請確保自己是使用python 3.10.6)
python src/modules/main.py                                # 執行程式
```
### 📁 文件結構
```
.
├── ...
├── src/modules                    # 主程式資料夾
│   ├── main.py                    # 主程式，負責整個程式的運行
│   ├── main_view.py               # 主要視圖，負責視覺化
│   ├── ui_logic.py                # 主視圖的邏輯，負責程式的運行
│   ├── function.py                # 功能函式，負責功能實現
│   ├── log_view.py                # 日誌視圖，負責日誌的顯示
│   ├── process_view.py            # 流程視圖，負責流程的處理和視覺化
│   └── clicking_functions.py      # 處理ClickWorker2相關的點擊功能實現
└── ...
```

### 🏫 這是高三專題實作，僅供學術研究使用

編程者 : ATGXicefires & wj6wj6(Koyana) & Creeperlol

### ⚠️ 注意事項

請確保圖片解析度與要偵測的畫面一樣

例如: 偵測1920x1080的畫面，圖片要從1920x1080的畫面擷取
裁切圖片不影響偵測，但縮放圖片會影響偵測
