import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)')
idx2 = s.find('lista_chats_html +=', idx)
print(s[idx:idx2+600])
