import sys
with open('whatsapp_client.py', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
for i in range(235, min(255, len(lines))):
    print(f"{i+1}: {lines[i]}")
