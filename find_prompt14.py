import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'MENSAJE_BIENVENIDA', s)
for m in matches:
    if m.start() > 1000:
        print(s[m.start()-200:m.end()+300])
        print('-'*20)
