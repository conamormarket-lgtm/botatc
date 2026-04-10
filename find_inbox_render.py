import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('def renderizar_inbox')
print(s[idx:idx+1500])
