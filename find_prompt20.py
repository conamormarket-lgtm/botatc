import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('bot_atc.py', 'r', encoding='utf-8').read()
idx = s.find('generar_respuesta')
if idx == -1: idx = s.find('def generar_')
print(s[idx:idx+2500])
