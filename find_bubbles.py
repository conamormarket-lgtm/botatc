import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('for i, m in enumerate(msgs):')
print(s[idx:idx+1500])
