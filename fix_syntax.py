import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the injected escaped quotes
if '\\"\\"\\"' in text:
    text = text.replace('\\"\\"\\"', '\"\"\"')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed escaped quotes")
