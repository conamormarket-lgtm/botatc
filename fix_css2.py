import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace all occurrences of max-width: 250px with width: 250px; max-width: 100%; box-sizing: border-box;
rep1 = r"""<img src="{src_url}" onclick="window.open('{src_url}', '_blank')" style="max-width: 250px; max-height: 300px; border-radius: 8px; object-fit: cover; margin-bottom: 5px; cursor: zoom-in;"""
to1 = r"""<img src="{src_url}" onclick="window.open('{src_url}', '_blank')" style="width: 250px; max-width: 100%; max-height: 300px; border-radius: 8px; object-fit: cover; margin-bottom: 5px; cursor: zoom-in; box-sizing: border-box;"""

rep2 = r"""<video controls src="{src_url}" style="max-width: 250px; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px;"""
to2 = r"""<video controls src="{src_url}" style="width: 250px; max-width: 100%; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; box-sizing: border-box;"""

rep3 = r"""<audio controls src="{src_url}" style="max-width: 250px; height: 40px; outline: none; margin-bottom: 5px;"""
to3 = r"""<audio controls src="{src_url}" style="width: 250px; max-width: 100%; height: 40px; outline: none; margin-bottom: 5px; box-sizing: border-box;"""

if rep1 in text: text = text.replace(rep1, to1)
if rep2 in text: text = text.replace(rep2, to2)
if rep3 in text: text = text.replace(rep3, to3)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

with open("inbox.html", "r", encoding="utf-8") as f:
    inbox = f.read()

if "overflow-x: hidden;" not in inbox:
    target = r"""    <style>
        :root {"""
    inbox = inbox.replace(target, r"""    <style>
        body { overflow-x: hidden; }
        :root {""")
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(inbox)

print("Applied container responsive fixes!")
