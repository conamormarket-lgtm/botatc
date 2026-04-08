import re
with open("server.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'enviar_manual_endpoint', s)
if m:
    print(s[m.end():m.end()+2500])
else:
    print("Not found input container in server.py")
