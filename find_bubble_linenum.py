import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()
import re

# find line number where burbujas += is
m = re.search(r'burbujas \+= f\'<div class="bubble', ss)
if m:
    linenum = ss[:m.start()].count('\n') + 1
    print(f"Line {linenum}")
    print(ss[m.start():m.start()+300])
