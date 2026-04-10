import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'contacts', s)
for m in matches:
    print(s[m.start()-50:m.end()+150])
    print('-'*20)
