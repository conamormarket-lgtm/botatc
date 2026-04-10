import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
chunk = ss[idx:idx+10000]
# Search for the final msg_html string containing timestamp
patterns2 = ['timestamp', 'msg_id', 'hora', 'status', 'palomita']
for p in patterns2:
    idx2 = chunk.find(p)
    print(f"'{p}' at {idx2}")
    if idx2 != -1:
        print(chunk[max(0,idx2-50):idx2+200])
    print()
