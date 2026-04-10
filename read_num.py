import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('if not (enviado_ahora and enviado_ahora')
idx2 = text.find('numero_wa =', idx-1000)
if idx2 != -1:
    print(text[idx2:idx2+600])
else:
    print("Not found")
