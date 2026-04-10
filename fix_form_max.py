import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target1 = r"""<form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center;">"""
rep1 = r"""<form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center; box-sizing:border-box; max-width:100%; overflow:hidden;">"""


if target1 in text:
    text = text.replace(target1, rep1)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched form!")
else:
    print("Form not found")

