import json

# 打開 JSON 檔案
with open('SaveData/connections.json', 'r') as file:
    data = json.load(file)  # 解析 JSON 內容為 Python 字典

# 輸出讀取的內容
print(data)

# 訪問具體內容
# steps = data['steps']
# print(steps['Step1'])  # 1.png

# 只擷取 steps 的內容
steps_content = data.get('steps', {})  # 使用 .get() 以避免 KeyError

# 輸出 steps 的內容
print(steps_content)

# step1_image = data['steps']['Step1']
# print(step1_image)