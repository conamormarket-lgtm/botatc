import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('{grupo_virtual_banner}')
print("FOUND:", idx)
print(s[max(0,idx-200):max(len(s), idx+500)])
