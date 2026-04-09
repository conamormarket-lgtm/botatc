import re
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'# Construir historial de mensajes.*?if texto_renderizado\.endswith\(', text, flags=re.DOTALL)
if m:
    print(m.group(0))
else:
    print("Not found")
