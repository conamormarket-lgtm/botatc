import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
idx = s.find('sidebar')
if idx == -1: idx = s.find('header')
print(s[idx:idx+800])
