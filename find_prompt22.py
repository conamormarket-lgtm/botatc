import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
import re
# check where `nombre` from WhatsApp contacts is injected into `historial`.
matches = re.finditer(r'historial', s)
for m in matches:
    if 'nombre' in s[m.start()-100:m.end()+100] and 'system' in s[m.start()-100:m.end()+100]:
        print("FOUND:")
        print(s[m.start()-100:m.end()+100])
