import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        .chat-viewer-panel {
            flex: 1;
            background-color: var(--bg-main);
            display: flex;
            flex-direction: column;
            position: relative;
            min-width: 0;
            /* previene desbordamiento en flex */
        }"""

replacement = r"""        .chat-viewer-panel {
            flex: 1;
            background-color: var(--bg-main);
            display: flex;
            flex-direction: column;
            position: relative;
            min-width: 0;
            min-height: 0;
            /* previene desbordamiento en flex */
        }"""

if target in text:
    text = text.replace(target, replacement)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched min-height 0 successfully!")
else:
    print("Not found.")
