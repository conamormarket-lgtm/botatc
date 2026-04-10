import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('chat_viewer_html =')
if idx != -1:
    print(text[max(0, idx-200):idx+400])
else:
    print("Not found")
