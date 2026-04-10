import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix form overflow hidden
target1 = r"""<form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center; box-sizing:border-box; max-width:100%; overflow:hidden;">"""
rep1 = r"""<form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center; box-sizing:border-box; max-width:100%;">"""

if target1 in text: text = text.replace(target1, rep1)

# Fix wrapper overflow hidden
target2 = r"""<div style="padding:1rem 1rem;border-top:1px solid var(--accent-border);background:var(--accent-bg);width:100%;max-width:100vw;overflow:hidden;box-sizing:border-box;">"""
rep2 = r"""<div style="padding:1rem 1rem;border-top:1px solid var(--accent-border);background:var(--accent-bg);width:100%;max-width:100vw;box-sizing:border-box;">"""

if target2 in text: text = text.replace(target2, rep2)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

with open("inbox.html", "r", encoding="utf-8") as f:
    inbox = f.read()

# add overflow-x: hidden to chat viewer explicitly
target3 = r"""        .chat-viewer-panel {
            flex: 1;
            background-color: var(--bg-main);
            display: flex;
            flex-direction: column;
            position: relative;
            min-width: 0;
            min-height: 0;
            /* previene desbordamiento en flex */
        }"""
rep3 = r"""        .chat-viewer-panel {
            flex: 1;
            background-color: var(--bg-main);
            display: flex;
            flex-direction: column;
            position: relative;
            min-width: 0;
            min-height: 0;
            max-width: 100vw;
            overflow-x: hidden;
            /* previene desbordamiento en flex */
        }"""

if target3 in inbox:
    inbox = inbox.replace(target3, rep3)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(inbox)

print("Fixed over-eager hidden!")
