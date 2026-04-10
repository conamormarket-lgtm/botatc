import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('def renderizar_inbox')
idx2 = s.find('s = sesiones[wa_id]', idx)
print(s[max(0,idx2-200):idx2+300])
