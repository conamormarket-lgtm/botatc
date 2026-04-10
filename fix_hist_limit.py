import sys

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'hist_total[-5:]'
rep = 'hist_total[-50:]'

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced hist limit")
else:
    print("Target not found")
