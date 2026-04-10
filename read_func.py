import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('async def recibir_mensaje')
if idx != -1:
    print(text[idx:idx+800])
else:
    print("Not found")
