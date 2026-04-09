with open("server.py", "r", encoding="utf-8") as f:
    text = f.readlines()
for i, line in enumerate(text):
    if "document" in line.lower():
        print(f"{i}: {line.strip()}")
