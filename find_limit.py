import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('hist_total[-5:]')
print(s[max(0,idx-200):idx+300])
