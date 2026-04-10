import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Replace exactly `<div class="chat-input-area"` with `<div class="chat-input-area" {style_input_area}` 
# And add `{grupo_virtual_banner}` right before it.

if '{style_input_area}' not in text:
    text = re.sub(
        r'<div[^>]*class="chat-input-area"[^>]*>', 
        r'{grupo_virtual_banner}\n\g<0>'[:-1] + ' {style_input_area}>', 
        text
    )
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected input area placeholders via regex")
else:
    print("Already injected")
