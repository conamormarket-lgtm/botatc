import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'@app\.post\(\"/webhook\"?\)', s)
if m:
    print(s[m.start():m.start()+1500])
else:
    print("Not found init bubble in server.py")
