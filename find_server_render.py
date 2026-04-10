import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# The chat is likely rendered server-side. Check server.py for HTML generation of messages
ss = open('server.py', 'r', encoding='utf-8').read()

patterns = ['bubble-bot', 'bubble-user', 'lado-der', 'lado-izq']
for p in patterns:
    matches = [(m.start()) for m in re.finditer(p, ss)]
    print(f"server.py '{p}': {len(matches)} occurrences")
    if matches:
        print(ss[max(0, matches[0]-100):matches[0]+400])
    print()
