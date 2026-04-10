import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"<style>"
replacement = r"""<style>
        * { box-sizing: border-box; }
        body { overflow-x: hidden; max-width: 100vw; }"""

if target in text:
    text = text.replace(target, replacement, 1) # match first one
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected global border-box and overflow-x!")
else:
    print("Target not found.")

