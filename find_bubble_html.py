import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
# Find the final HTML structure of each bubble
print(ss[idx+4000:idx+6000])
