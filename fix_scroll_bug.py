import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        .chat-viewer-panel {
            flex: 1;
            display: flex;"""

replacement = r"""        .chat-viewer-panel {
            flex: 1;
            display: flex;
            min-height: 0;
            min-width: 0;"""

if target in text:
    text = text.replace(target, replacement)
    
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched min-height: 0 flexbox bug!")
else:
    print("Target not found.")

