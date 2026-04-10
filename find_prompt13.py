import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('MENSAJE_BIENVENIDA', s.find('from prompts') + 50)
print(s[max(0,idx-200):idx+500])
