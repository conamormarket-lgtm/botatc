import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
idx = s.find('<a href="/settings"')
print(s[idx-50:idx+300])
