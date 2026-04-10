import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
chunk = ss[idx:idx+14000]
print(chunk[10000:12000])
