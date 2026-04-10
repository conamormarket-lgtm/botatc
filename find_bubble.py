import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

for i, line in enumerate(text.split('\n')):
    if "bubble" in line.lower():
        print(f"Line {i}:", line)
