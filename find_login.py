import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'def login', s)
for m in matches:
    print(s[max(0, m.start()-200):min(len(s), m.end()+200)])
    print("="*40)
