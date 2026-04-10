import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = 25453
print(s[max(0,idx-200):idx+200])
