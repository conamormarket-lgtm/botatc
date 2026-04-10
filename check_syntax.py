import sys
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i in range(830, min(len(lines), 850)):
    print(f"{i+1}: {lines[i]}")
