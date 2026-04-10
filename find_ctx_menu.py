import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the existing context menu
patterns = ['ctx-menu', 'ctx-item', 'Responder Nativamente', 'contextmenu']
for p in patterns:
    idx = s.find(p)
    if idx != -1:
        print(f"=== '{p}' at {idx}: ===")
        print(s[max(0,idx-100):idx+400])
        print()
