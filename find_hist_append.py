import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('@app.post("/api/admin/enviar_manual")')
chunk = ss[idx:idx+4000]
# Find where message is appended to historial
idx2 = chunk.find('historial')
if idx2 != -1:
    print(chunk[max(0,idx2-200):idx2+600])
