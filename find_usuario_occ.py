import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
ss = open('server.py', 'r', encoding='utf-8').read()

matches = [m.start() for m in re.finditer('usuario', ss, re.IGNORECASE)]
print(f"{len(matches)} matches")
for m in matches[:8]:
    print(f"--- at {m} (line {ss[:m].count(chr(10))+1}):")
    print(ss[m:m+100])
    print()
