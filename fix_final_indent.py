import sys
with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(3372, 3376):
    if lines[i].startswith("            "):
        lines[i] = lines[i][4:]

with open('server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Fixed indent")
