import re
with open("whatsapp_client.py", "r", encoding="utf-8") as f:
    s = f.read()

m = re.search(r'def enviar_media', s)
if m:
    print(s[m.start():m.start()+1500])
else:
    print("Not found input container in server.py")
