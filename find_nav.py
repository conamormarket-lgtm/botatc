import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
idx = s.find('<nav class="sidebar">')
print(s[idx:idx+800])
