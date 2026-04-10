import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('app = FastAPI')
if idx == -1: idx = s.find('app')
print(s[max(0,idx-100):idx+200])
