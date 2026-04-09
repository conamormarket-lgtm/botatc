import re

with open("server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, x in enumerate(lines):
    if "def wrap_phone" in x or 'texto  = m["content"].replace' in x or 'texto     = m["content"].replace' in x:
        print(f"{i}: {x}", end="")
