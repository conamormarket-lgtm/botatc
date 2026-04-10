import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('firebase_client.py', 'r', encoding='utf-8').read()
idx = s.find('def inicializar_firebase()')
print(s[max(0,idx-200):idx+500])
