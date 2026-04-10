import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
# Find the HTML append - the final f-string that outputs the bubble div
chunk = ss[idx:idx+10000]
# Look for where the bubble is created with its data attributes
idx2 = chunk.find('data-msg-id')
if idx2 != -1:
    print(chunk[max(0,idx2-200):idx2+800])
else:
    # search for the final html string pattern
    idx2 = chunk.find('msg_html +=')
    if idx2 != -1:
        print(chunk[idx2:idx2+2000])
