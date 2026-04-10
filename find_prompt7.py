import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('prompts.py', 'r', encoding='utf-8').read()
idx = s.find('if datos_pedido:')
print(s[idx+700:idx+1500])
