import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the main renderMessages/loadChat JS function
patterns = ['function renderMessages', 'function cargarChat', 'function loadMessages', 'function renderChat', 'appendMessage', 'function formatMsg']
for p in patterns:
    idx = s.find(p)
    if idx != -1:
        print(f"Found '{p}' at {idx}:")
        print(s[idx:idx+300])
        print()
