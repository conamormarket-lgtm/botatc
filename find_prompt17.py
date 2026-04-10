import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'nombre', s)
for m in matches:
    if 24000 < m.start() < 27000:
        print(s[m.start()-50:m.end()+60])
        print('-'*20)
