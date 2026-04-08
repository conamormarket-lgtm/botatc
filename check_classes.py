import re
with open("inbox.html", "r", encoding="utf-8") as f:
    s = f.read()

for match in re.findall(r'className\s*=\s*[\"\'][a-zA-Z0-9_\-\s]*[\"\']', s):
    print(match)
