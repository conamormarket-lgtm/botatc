import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""    <style>
        body { overflow-x: hidden; }
        :root {"""

replacement = r"""    <style>
        * { box-sizing: border-box; }
        body { overflow-x: hidden; }
        :root {"""

if target in text:
    text = text.replace(target, replacement)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Added global border-box!")
else:
    print("Target not found.")
