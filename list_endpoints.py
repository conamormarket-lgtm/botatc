import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'@app\.(get|post|delete)\(.[^"\n]+"\)', s)
for m in matches:
    print(m.group(0))
