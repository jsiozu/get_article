import json

with open('./ip_list.json', encoding='utf-8') as f:
    data = json.load(f)

print(data)
