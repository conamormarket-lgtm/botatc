import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('elif tipo_mensaje == "location":')
if idx != -1:
    print(text[max(0, idx-500):idx+500])
else:
    print("Not found")
