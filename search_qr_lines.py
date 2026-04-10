import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()
lines = s.split('\n')

# Search for any mention of quick/reply/respuesta in JS context 
keywords = ['title', 'quick', 'reply', 'rápida']
for i, line in enumerate(lines):
    for kw in keywords:
        if kw.lower() in line.lower() and ('fetch' in line.lower() or 'enviar' in line.lower() or 'texto' in line.lower()):
            print(f"Line {i+1}: {line[:120]}")
            break
