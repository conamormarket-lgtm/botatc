import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()
import re

# find where wamid_attr is used  
matches = [m for m in re.finditer('wamid_attr', ss)]
for m in matches[:5]:
    print(ss[max(0,m.start()-50):m.start()+200])
    print()
