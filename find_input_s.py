import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
for line in s.split('\n'):
    if 'chat-input-area' in line:
        print(line)
