import sys
import re
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()

matches = re.finditer(r'get_system_prompt\([^\)]*\)', s)
for m in matches:
    start = max(0, m.start() - 50)
    end = min(len(s), m.end() + 50)
    print("Match at", m.start(), ":")
    print(s[start:end])
    print("-" * 40)
