import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
lines = s.split('\n')
for line in lines:
    if 'datos_pedido' in line:
        print(line.strip())
