import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'@app\.get\(\"/inbox', s)
if m:
    print(s[m.start():m.end()+1500])
else:
    print("Not found input container in server.py")
