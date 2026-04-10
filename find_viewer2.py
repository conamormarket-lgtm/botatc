import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('''    elif wa_id and (wa_id in sesiones) and len(sesiones[wa_id].get("historial", [])) == 0:''')
print(s[idx:idx+1500])
