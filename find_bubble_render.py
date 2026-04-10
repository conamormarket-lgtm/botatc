import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()

idx = 37892
print(s[max(0,idx-500):idx+2000])
