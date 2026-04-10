import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('s = sesiones[wa_id]')
print(s[max(0,idx-200):idx+300])
