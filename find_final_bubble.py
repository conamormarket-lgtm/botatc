import sys
sys.stdout.reconfigure(encoding='utf-8')
ss = open('server.py', 'r', encoding='utf-8').read()

idx = ss.find('for m in msgs:\n            es_bot = m["role"]')
chunk = ss[idx:idx+10000]
print(chunk[9600:9600+2500])
