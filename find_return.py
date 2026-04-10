import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('return HTMLResponse(html)')
if idx == -1: idx = s.find('HTMLResponse(content')
print(s[max(0,idx-200):max(len(s), idx+500)])
