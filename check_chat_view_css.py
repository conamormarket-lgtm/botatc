import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'chat_view_css\s*=(\s*f?\"\"\".*?\"\"\")', s, re.DOTALL)
if m:
    print(m.group(1)[:1000])
else:
    print("Not found chat_view_css in server.py")
