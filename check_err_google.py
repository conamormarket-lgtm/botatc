import sys
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i in range(865, 890):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}")
