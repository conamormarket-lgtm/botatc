import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Modify `todas` loop list in renderizar_inbox
target_todas = """    # Procesar Lista de Chats
    todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)
    lista_chats_html = "" """

rep_todas = """    # Procesar Lista de Chats
    grupos_sesiones = []
    for vg in global_groups:
        miembros = vg.get("members", [])
        sesiones_miembros = [sesiones.get(m) for m in miembros if m in sesiones]
        if not sesiones_miembros: continue
        vg_ultima_actividad = max((s.get("ultima_actividad", datetime.utcnow()) for s in sesiones_miembros))
        
        hist_total = []
        for s in sesiones_miembros:
            hist_total.extend(s.get("historial", []))
        hist_total.sort(key=lambda x: x.get("timestamp", ""))
        
        s_fake = {
            "ultima_actividad": vg_ultima_actividad,
            "nombre_cliente": f"👥 {vg.get('name')}",
            "bot_activo": True,
            "historial": hist_total[-5:],
            "is_virtual_group": True,
            "vg_id": vg.get("id"),
            "etiquetas": []
        }
        grupos_sesiones.append((vg.get("id"), s_fake))

    todas = sorted(list(sesiones.items()) + grupos_sesiones, key=lambda x: x[1].get("ultima_actividad", datetime.min), reverse=True)
    lista_chats_html = "" """

if target_todas in text:
    text = text.replace(target_todas, rep_todas)
    print("Injected virtual session generation to 'todas'")
else:
    print("target_todas not found")

# 2. Add is_virtual_group styling in chat list loop
target_badge = """        badge_html = '<span class="badge">🟢 Bot Activo</span>'
        if not activo:
            badge_html = '<span class="badge badge-alert">🔴 Esperando</span>'"""

rep_badge = """        is_vg = s.get("is_virtual_group", False)
        if is_vg:
            badge_html = '<span class="badge" style="background:rgba(168, 85, 247, 0.15); color:#a855f7; border: 1px solid rgba(168, 85, 247, 0.3);">👥 GRUPO VIRTUAL</span>'
        else:
            badge_html = '<span class="badge">🟢 Bot Activo</span>'
            if not activo:
                badge_html = '<span class="badge badge-alert">🔴 Esperando</span>'"""

if target_badge in text: text = text.replace(target_badge, rep_badge)

# 3. Intercept `wa_id` parser in `chat_viewer_html`
target_chat_viewer = """    chat_viewer_html = ""
    chat_view_css = ""
    
    # Auto-inicializar chat nuevo si se manda un número válido (ej. desde el buscador UI)
    if wa_id and wa_id not in sesiones:"""

rep_chat_viewer = """    chat_viewer_html = ""
    chat_view_css = ""
    s_fake_vg = None
    
    if wa_id and wa_id.startswith("vg_"):
        vg = next((g for g in global_groups if g.get("id") == wa_id), None)
        if vg:
            s_fake_vg = {
                "is_virtual_group": True,
                "nombre_cliente": f"👥 {vg.get('name')}",
                "historial": [],
                "bot_activo": True,
                "ultima_actividad": datetime.utcnow()
            }
            miembros = vg.get("members", [])
            for m in miembros:
                if m in sesiones:
                    hist = sesiones[m].get("historial", [])
                    nombre_m = sesiones[m].get("nombre_cliente") or m
                    for msg in hist:
                        msg_copy = dict(msg)
                        msg_copy["sender_name_override"] = nombre_m
                        msg_copy["sender_wa_id"] = m
                        s_fake_vg["historial"].append(msg_copy)
            s_fake_vg["historial"].sort(key=lambda x: x.get("timestamp", ""))
            
            if not s_fake_vg["historial"]:
                chat_viewer_html = f'''<div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--text-muted);font-size:0.95rem;flex-direction:column;gap:10px;">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    <p>Grupo Virtual "{vg.get('name')}".</p><p>Todavía no hay mensajes correspondientes a sus miembros.</p>
                </div>'''

    # Auto-inicializar chat nuevo si se manda un número válido (ej. desde el buscador UI)
    elif wa_id and wa_id not in sesiones:"""

if target_chat_viewer in text: text = text.replace(target_chat_viewer, rep_chat_viewer)

# 4. Modify the rest of `wa_id` logic to use `s_fake_vg` if available
# Instead of replacing specific huge parts, we can just find 'if not wa_id or wa_id not in sesiones:'
# Wait, `elif wa_id and (wa_id in sesiones) and len(sesiones[wa_id].get("historial", [])) == 0:`
# We must replace them manually.
text = text.replace('if not wa_id or wa_id not in sesiones:', 'if not wa_id or (wa_id not in sesiones and not s_fake_vg):')

# Find `s = sesiones[wa_id]` inside `else:` block of `chat_viewer_html` to use `s_fake_vg`!
# Let's see the exact text.
import re
text = re.sub(r'else:\n\s+s = sesiones\[wa_id\]', 'else:\n        s = s_fake_vg if s_fake_vg else sesiones[wa_id]', text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Injected inbox generation logic")
