import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the existing context menu HTML div
idx = s.find('<div class="ctx-item" id="ctxReply"')
print(s[max(0,idx-400):idx+200])
