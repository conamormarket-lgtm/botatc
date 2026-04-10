import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the hardcoded color from BOTH wrap_phone and wrap_phone2
target = """style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;\""""
rep = """style="text-decoration:underline; cursor:pointer; font-weight:bold;\""""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced hardcoded inline phone highlight in server.py")
else:
    print("Target not found in server.py")

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Add a CSS rule to inbox.html
target_css = """        /* Base Styles */"""
rep_css = """        /* Base Styles */
        .bubble-user .chat-phone { color: var(--primary-color) !important; }
        .bubble-bot .chat-phone { color: #ffffff !important; opacity: 0.9; }"""

if target_css in text:
    text = text.replace(target_css, rep_css)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected CSS into inbox.html")
else:
    print("Target CSS not found in inbox.html")
