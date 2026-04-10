import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('@app.post("/api/admin/enviar_manual")')
print(ss[idx:idx+1500])
