import json

# 讀取 JSON 檔案
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# 寫入 JSON 檔案
def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 使用範例
if __name__ == "__main__":
    # 更新檔案路徑
    file_path = 'test/data.json'
    
    # 讀取 JSON
    data = read_json(file_path)
    print("讀取的資料：", data)
    
    # 修改資料
    data['new_key'] = 'new_value'
    
    # 寫入 JSON
    write_json(file_path, data)
    print("已更新資料並寫入檔案。")
