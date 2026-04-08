import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()
m = re.search(r'@app\.get\(\"/inbox', s)
if m:
    print(s[max(0, m.start()-100):m.start()+2000])
else:
    print("Not found inbox endpoint")
