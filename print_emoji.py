import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('id="emojiMenu"')
print("idx1:", idx1)
if idx1 != -1:
    print(text[max(0, idx1-200):idx1+500])
