with open("server.py", "r", encoding="utf-8") as f:
    text = f.readlines()
for i, line in enumerate(text):
    if "tipo_mensaje" in line and ("audio" in line or "voice" in line or "document" in line):
        end = min(i + 5, len(text))
        print("".join(text[i-1:end]))
