import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()

lines = s.split('\n')
for i, line in enumerate(lines):
    if 'sort(' in line or 'sorted(' in line:
        print(f"Line {i+1}: {line.strip()}")
