import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

def replacer(match):
    s = match.group(0)
    s = "{grupo_virtual_banner}\n" + s[:-1] + " {style_input_area}>"
    return s

if '{style_input_area}' not in text:
    text = re.sub(r'<div[^>]*class="chat-input-area"[^>]*>', replacer, text)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected input area placeholders via regex")
else:
    print("Already injected")
