import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'<script.*?firebase.*?>', s)
for m in matches:
    print(m.group(0))
