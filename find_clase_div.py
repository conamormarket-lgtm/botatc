import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
chunk = ss[idx:idx+10000]
# Find the bubble div creation
idx2 = chunk.find('<div class=\\"{clase}')
if idx2 == -1:
    idx2 = chunk.find(f'clase} {lado}')
if idx2 == -1:
    idx2 = chunk.find('{clase}')
    
print(f"found at {idx2}")
if idx2 != -1:
    print(chunk[max(0,idx2-100):idx2+1000])
