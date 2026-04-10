import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('whatsapp_client.py', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'(template|plantilla)', s, re.IGNORECASE)
for m in matches:
    print(s[m.start()-100:m.end()+250])
    print('-'*20)
