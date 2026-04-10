import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find where messages are rendered with bubble-user or bubble-bot class
patterns = ['bubble-user', 'role.*assistant', 'msg.role', 'historial']
for p in patterns:
    matches = [(m.start()) for m in re.finditer(p, s)]
    print(f"'{p}': {len(matches)} occurrences - first at {matches[0] if matches else 'none'}")
    if matches:
        print(s[max(0, matches[0]-50):matches[0]+200])
    print()
