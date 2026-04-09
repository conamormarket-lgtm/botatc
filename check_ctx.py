import re

with open("inbox.html", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'document\.addEventListener\("contextmenu".*?\}\);', s, flags=re.DOTALL)
if m:
    print(m.group(0))
else:
    print("Not found document")

m2 = re.search(r'chatWin\.addEventListener\("contextmenu".*?\}, true\);', s, flags=re.DOTALL)
if m2:
    print(m2.group(0))
else:
    print("Not found chatwin")
