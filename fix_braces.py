import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """{ document.getElementById('btnTabEmoji').click(); if(window.cargarStickers) window.cargarStickers(); }"""
rep = """{{ document.getElementById('btnTabEmoji').click(); if(window.cargarStickers) window.cargarStickers(); }}"""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed f-string braces")
else:
    print("Target not found.")
