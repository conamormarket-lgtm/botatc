import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('elif tipo == "imagen":')
print(text[max(0, idx-50):max(0, idx+500)])
