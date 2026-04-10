import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('prompts.py', 'r', encoding='utf-8').read()
idx = s.find('if isinstance(datos_pedido, list):')
if idx == -1: idx = s.find('datos_pedido')
print(s[idx:idx+1500])
