import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# find the JS function that renders messages
idx = s.find('function renderMessage')
if idx == -1:
    idx = s.find('function renderChat')
if idx == -1:
    idx = s.find('bubble-bot')
    # find all occurrences
    matches = [m.start() for m in re.finditer('bubble-bot', s)]
    for m in matches[:3]:
        print(f"--- at {m}:")
        print(s[max(0,m-50):m+200])
        print()
else:
    print(s[idx:idx+1000])
