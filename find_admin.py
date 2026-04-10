import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('@app.get("/admin", response_class=HTMLResponse)')
print(s[idx:idx+800])
