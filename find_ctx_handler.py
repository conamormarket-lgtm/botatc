import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the contextmenu event handler and the full context menu div
idx = s.find('document.addEventListener("contextmenu"')
chunk = s[idx:idx+3000]
print(chunk)
