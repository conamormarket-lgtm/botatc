import sys

with open("whatsapp_client.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i == 244 and line.strip() == "}":
        continue
    new_lines.append(line)

with open("whatsapp_client.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
    
print("Removed extra bracket")
