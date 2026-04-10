import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('firebase_client.py', 'r', encoding='utf-8').read()
idx = s.find('def cargar_grupos_bd')
print(s[idx:idx+500])
