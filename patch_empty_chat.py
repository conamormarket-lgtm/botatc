import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""    if not wa_id or wa_id not in sesiones:
        chat_viewer_html = \"\"\"
        <div class="empty-state">"""

replacement = r"""    elif wa_id and (wa_id in sesiones) and len(sesiones[wa_id].get("historial", [])) == 0:
        chat_viewer_html = f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:0.95rem;flex-direction:column;gap:10px;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <p>Nuevo chat inicializado.<br>Escribe tu primer mensaje abajo para saludar a <b>+{wa_id}</b>.</p>
        </div>'''
        
    if not wa_id or wa_id not in sesiones:
        chat_viewer_html = \"\"\"
        <div class="empty-state">"""

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched empty chat viewer!")
else:
    print("Target not found exactly")
