import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

idx = s.find('enviar_manual')
print(s[max(0,idx-200):idx+800])
