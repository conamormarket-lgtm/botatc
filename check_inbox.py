import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()
m = re.search(r'def inbox\(', s)
if m:
    print(s[max(0, m.start()-100):m.start()+1500])
else:
    print("Not found def inbox")
