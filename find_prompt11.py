import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('sesion["historial"].append({"role": "user", "content":')
if idx == -1: idx = s.find('sesion["historial"].append(')
print(s[max(0,idx-200):idx+500])
