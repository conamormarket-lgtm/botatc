import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('@app.post("/api/admin/enviar_manual")')
chunk = ss[idx:idx+5000]

# find all 'historial' in chunk
import re
matches = [m.start() for m in re.finditer('historial', chunk)]
for m in matches:
    print(f"--- at {m}:")
    print(chunk[max(0,m-100):m+400])
    print()
