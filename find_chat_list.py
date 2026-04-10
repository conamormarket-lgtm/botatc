import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
import re
matches = re.finditer(r'<div class="chat-list', s)
for m in matches:
    print(s[m.start()-200:m.start()+400])
