import sys, re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('L.nea Secundaria', 'Linea Secundaria')

load_aliases = '''    import json
    aliases = {}
    try:
        with open('line_aliases.json', 'r', encoding='utf-8') as fa:
            aliases = json.load(fa)
    except: pass
'''
text = re.sub(r'(def renderizar_inbox[^\:]+\:\n)', r'\1' + load_aliases, text, count=1)

line_html = r'''
    active_line_name = "Todas las Líneas" if line_filter == "all" else aliases.get(line_filter, "Línea QR" if line_filter != "principal" else "Línea Principal")

    labels_filter_html = f"""
    <div style="position:relative; margin-top:1rem; text-align:left; display:flex; gap:0.5rem; align-items:center;">
        
        <button type="button" onclick="const m = document.getElementById('inboxLineMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            {active_line_name}
        </button>

        <div id="inboxLineMenu" style="display:none; position:absolute; top:calc(100% + 0.5rem); left:0; width:100%; max-width:250px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:8px; box-shadow:0 8px 16px rgba(0,0,0,0.5); flex-direction:column; z-index:100; overflow:hidden;">
            <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={unread or ''}&line=all" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if line_filter == 'all' else 'transparent'};">Todas las Líneas</a>
            <a href="{base_url}?tab={tab}&label={label_filter or ''}&unread={unread or ''}&line=principal" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{'var(--primary-color)' if line_filter == 'principal' else 'transparent'};">Línea Principal</a>
"""
    for q_id, q_name in aliases.items():
        labels_filter_html += f'<a href="{{base_url}}?tab={{tab}}&label={{label_filter or ""}}&unread={{unread or ""}}&line={{q_id}}" style="padding:0.6rem 1rem; color:var(--text-main); text-decoration:none; display:flex; align-items:center; border-bottom:1px solid var(--accent-border); font-size:0.85rem; background:{"var(--primary-color)" if line_filter == q_id else "transparent"};">{q_name}</a>'
        
    labels_filter_html += "</div>"
'''
text = re.sub(r'labels_filter_html = f"""\s*<div style="position:relative; margin-top:1rem; text-align:left; display:flex; gap:0.5rem; align-items:center;">', line_html + r'\n    labels_filter_html += f"""\n        <button type="button" onclick="const m = document.getElementById(\'inboxFilterMenu\'); m.style.display = m.style.display===\'none\'?\'flex\':\'none\';" style="background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:16px; padding:0.4rem 1rem; color:var(--text-main); font-size:0.8rem; cursor:pointer; display:inline-flex; align-items:center; gap:0.5rem; font-weight:600;">', text)

loop_content_matcher = r'        if is_unread:\n            hist_sin_sys = \[m for m in s.get\("historial", \[\]\) if m\["role"\] != "system"\]\n            if not hist_sin_sys or hist_sin_sys\[-1\]\["role"\] != "user":\n                continue'

filter_logic = r'''        if is_unread:
            hist_sin_sys = [m for m in s.get("historial", []) if m["role"] != "system"]
            if not hist_sin_sys or hist_sin_sys[-1]["role"] != "user":
                continue
                
        # FILTRO DE LINEA MULTIPLE
        ch_line = s.get("lineId", "principal")
        if line_filter != "all" and ch_line != line_filter:
            continue
            
        line_alias = aliases.get(ch_line, "Línea Secundaria" if ch_line != "principal" else "")
        badge_line = f'<span style="font-size:0.65rem; background:rgba(255,255,255,0.05); padding:2px 6px; border-radius:4px; margin-left:0.5rem; border:1px solid rgba(255,255,255,0.1); color:var(--text-muted);">{line_alias}</span>' if ch_line != "principal" else ""
'''
text = re.sub(loop_content_matcher, filter_logic, text)

# Inject badge_line
inject_badge = r'<span class="chat-name">{pin_html}{nombre}{badge_line}</span>'
text = re.sub(r'<span class="chat-name">\{pin_html\}\{nombre\}</span>', inject_badge, text)

# Fix duplicated inbox_chat signatures by deleting old ones, and inserting clean ones.
text = re.sub(r'@app\.get\("/inbox"\).+?return renderizar_inbox[^\n]+', '', text, flags=re.DOTALL)
text = re.sub(r'@app\.get\("/inbox/\{wa_id\}"\).+?return renderizar_inbox[^\n]+', '', text, flags=re.DOTALL)

routes = '''
@app.get("/inbox")
async def inbox_main(request: Request, tab: str = "all", label: str = None, unread: str = None, line: str = "all"):
    return renderizar_inbox(request, None, tab, label, unread, line)

@app.get("/inbox/{wa_id}")
async def inbox_chat(request: Request, wa_id: str, tab: str = "all", label: str = None, unread: str = None, line: str = "all"):
    return renderizar_inbox(request, wa_id, tab, label, unread, line)
'''
text = text.replace('def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, \nunread: str = None):', routes + '\ndef renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, unread: str = None, line_filter: str = "all"):')
text = text.replace('def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, unread: str = None):', routes + '\ndef renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, unread: str = None, line_filter: str = "all"):')


with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
