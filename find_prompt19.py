import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'\[Nombre del cliente', s)
for m in matches:
    print("Match 1:")
    print(s[m.start()-100:m.end()+150])

matches2 = re.finditer(r'cliente:', s)
for m in matches2:
    print("Match 2:")
    print(s[m.start()-100:m.end()+150])
