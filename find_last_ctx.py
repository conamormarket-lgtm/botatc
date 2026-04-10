import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the last ctx-item in the context menu
matches = [m.start() for m in re.finditer('class="ctx-item"', s)]
print(f"Found {len(matches)} ctx-item divs")
for m in matches[-3:]:
    print(f"--- at {m}:")
    print(s[m:m+200])
    print()
