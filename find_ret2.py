import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('return HTMLResponse(html)', s.find('def renderizar_inbox'))
if idx == -1: idx = s.find('return HTMLResponse', s.find('def renderizar_inbox'))
print(s[max(0,idx-200):idx+500])
