import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = "global_labels: list = []"
rep = "global_labels: list = []\nglobal_groups: list = []"

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected global_groups var")
else:
    print("Could not find global_labels")
