import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""<input type="text" id="manualMsgInput" placeholder="Escribe un mensaje... (/)" style="flex:1;padding:0.8rem 1rem;border-radius:12px;border:1px solid var(--accent-border);background:var(--bg-main);color:var(--text-main);outline:none;font-size:0.95rem;font-family:var(--font-main);" """
replacement = r"""<input type="text" id="manualMsgInput" placeholder="Escribe un mensaje... (/)" style="flex:1;min-width:0;width:100%;padding:0.8rem 1rem;border-radius:12px;border:1px solid var(--accent-border);background:var(--bg-main);color:var(--text-main);outline:none;font-size:0.95rem;font-family:var(--font-main);box-sizing:border-box;" """

if target in text:
    text = text.replace(target, replacement)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed manualMsgInput overflow")
else:
    print("Not found msg input target")

# Also let's fix any padding in chat-box container pushing it out
target_box = r"""<div style="padding:1rem 1.5rem;border-top:1px solid var(--accent-border);background:var(--accent-bg);">"""
replacement_box = r"""<div style="padding:1rem 1rem;border-top:1px solid var(--accent-border);background:var(--accent-bg);width:100%;max-width:100vw;overflow:hidden;box-sizing:border-box;">"""
if target_box in text:
    text = text.replace(target_box, replacement_box)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed chat-box container overflow")
else:
    print("Not found chat box target")

