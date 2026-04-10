import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('ctxPhoneChat')
idx2 = text.find('addEventListener', idx)
print(text[max(0, idx2-100):max(0, idx2+500)])
