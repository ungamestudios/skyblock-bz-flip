import json
with open('test.txt', 'r') as f:
    x = json.load(f)
with open('test.json', 'w') as f:
    y = {}
    for (key, value) in x.items():
        y[key] = value['name']
    json.dump(y, f)