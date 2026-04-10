import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('firebase_client.py', 'r', encoding='utf-8').read()
idx = s.find('def buscar_pedido_por_telefono(telefono')
print(s[idx:idx+1500])
