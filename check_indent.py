import sys
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i in range(max(0, 3365), min(len(lines), 3385)):
    print(f"{i+1}: {lines[i]}")
