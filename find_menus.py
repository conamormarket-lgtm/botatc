import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('id="emojiMenu"')
if idx1 != -1: print("server.py:", text[max(0, idx1-50):idx1+500])

idx2 = text.find("id='emojiMenu'")
if idx2 != -1: print("server.py:", text[max(0, idx2-50):idx2+500])

with open("inbox.html", "r", encoding="utf-8") as f:
    text2 = f.read()

idx3 = text2.find('id="emojiMenu"')
if idx3 != -1: print("inbox.html:", text2[max(0, idx3-50):idx3+500])

idx4 = text2.find("id='emojiMenu'")
if idx4 != -1: print("inbox.html:", text2[max(0, idx4-50):idx4+500])
