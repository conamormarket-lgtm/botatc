import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('<div class="chat-input-container" style="display: none;">')
if idx != -1:
    print(text[idx:idx+1500])
else:
    print("Not found")
