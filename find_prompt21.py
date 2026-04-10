import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('generar_respuesta')
print("Is nombre_cliente passed to generar_respusta?", "nombre_cliente" in s[idx:idx+2000])
