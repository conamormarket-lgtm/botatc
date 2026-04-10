import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("id=\"attachMenu")
if idx != -1:
    print(text[max(0, idx-200):idx+800])
else:
    print("Not found")
