import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'nombre_ws', s)
for m in matches:
    print(s[m.start()-100:m.end()+200])
    print('-'*20)
