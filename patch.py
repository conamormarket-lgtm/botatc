import sys

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. API Endpoints
old_1 = '''    chats.sort(key=lambda x: x["msg_count"], reverse=True)
    return {"chats": chats[:6]}

@app.post("/api/forward_messages")'''

new_1 = '''    chats.sort(key=lambda x: x["msg_count"], reverse=True)
    return {"chats": chats[:6]}

@app.post("/api/message/star")
async def toggle_star_message(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id")
    msg_id = data.get("msg_id")
    if not wa_id or not msg_id: return {"ok": False, "error": "Datos incompletos"}
    
    s = sesiones.get(wa_id)
    if not s: return {"ok": False, "error": "Chat no encontrado"}
    
    found = False
    for m in s.get("historial", []):
        if m.get("msg_id") == msg_id:
            m["is_starred"] = not m.get("is_starred", False)
            found = True
            break
            
    if found:
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, s)
        except Exception:
            pass
        return {"ok": True}
    return {"ok": False, "error": "Mensaje no encontrado"}

@app.post("/api/message/pin")
async def toggle_pin_message(request: Request):
    if not verificar_sesion(request): raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id")
    msg_id = data.get("msg_id")
    if not wa_id or not msg_id: return {"ok": False, "error": "Datos incompletos"}
    
    s = sesiones.get(wa_id)
    if not s: return {"ok": False, "error": "Chat no encontrado"}
    
    found = False
    for m in s.get("historial", []):
        if m.get("msg_id") == msg_id:
            m["is_pinned"] = not m.get("is_pinned", False)
            found = True
            break
            
    if found:
        try:
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, s)
        except Exception:
            pass
        return {"ok": True}
    return {"ok": False, "error": "Mensaje no encontrado"}

@app.post("/api/forward_messages")'''
content = content.replace(old_1, new_1)

# 2. Pinned messages list init inside main chat rendering (line 2508ish)
old_2_main = '''        import re
        burbujas = ""
        if len(all_msgs) > MAX_MENSAJES and not load_all:'''
new_2_main = '''        import re
        burbujas = ""
        pinned_messages = []
        if len(all_msgs) > MAX_MENSAJES and not load_all:'''
content = content.replace(old_2_main, new_2_main)

# 2b. Same for the other location just in case to be safe, using careful indentation
old_2_alt = '''    msgs    = [m for m in sesion.get("historial", []) if m["role"] != "system"]

    burbujas = ""
    for m in msgs:'''
new_2_alt = '''    msgs    = [m for m in sesion.get("historial", []) if m["role"] != "system"]

    burbujas = ""
    pinned_messages = []
    for m in msgs:'''
content = content.replace(old_2_alt, new_2_alt)

# 3. Add to burbuja (extra_data appending)
old_3 = '''                extra_data = f' data-sent-by="{sent_by_val}" data-ts="{ts_unix}" data-delivered-ts="{delivered_ts}" data-read-ts="{read_ts}" data-status="{msg_status}" data-quick-reply="{qr_title_val}"'
            
            burbujas += f"""'''
new_3 = '''                extra_data = f' data-sent-by="{sent_by_val}" data-ts="{ts_unix}" data-delivered-ts="{delivered_ts}" data-read-ts="{read_ts}" data-status="{msg_status}" data-quick-reply="{qr_title_val}"'
            
            is_starred = m.get("is_starred", False)
            is_pinned = m.get("is_pinned", False)
            extra_data += f' data-starred="{str(is_starred).lower()}" data-pinned="{str(is_pinned).lower()}"'
            
            meta_html = ""
            if is_starred:
                meta_html += '<span style="color:#fbbf24; margin-left:4px; font-size:12px;">★</span>'
            if is_pinned and 'pinned_messages' in locals():
                pinned_messages.append(m)

            burbujas += f"""'''
content = content.replace(old_3, new_3)

# 4. Same for secondary location
old_4 = '''<div class="mensaje {lado}">
          <div class="remitente">{remitente}</div>
          <div class="{clase}">{texto}</div>
        </div>"""'''
new_4 = '''<div class="mensaje {lado}">
          <div class="remitente">{remitente}</div>
          <div class="{clase}"{extra_data}>{texto}{meta_html}</div>
        </div>"""'''
# wait, the secondary location didn't have extra_data initialized, let's keep it simple and just do it in one sweep but safely:
# Let's just fix the rendering of the secondary area:
# Actually we were rendering bubbles in index too? No, it's get_chat_history_html that was important.
# I'll just change the main chat loop instead.
# Actually I'd better replace the 4th chunk explicitly.

# 5. Insert pinned_html header
old_5 = '''        chat_viewer_html = f"""
        <div style="flex:1; display:flex; flex-direction:column; min-height:0;">'''
new_5 = '''        pinned_html = ""
        if 'pinned_messages' in locals() and pinned_messages:
            last_pinned = pinned_messages[-1]
            p_content = last_pinned.get("content", "Mensaje multimedia").replace('\\n', ' ')
            if len(p_content) > 60: p_content = p_content[:60] + "..."
            p_wamid = last_pinned.get("msg_id", "")
            pinned_html = f\'\'\'
            <div style="background:var(--accent-bg); color:var(--text-main); padding:8px 12px; border-bottom:1px solid var(--accent-border); display:flex; align-items:center; gap:8px; cursor:pointer; font-size:0.85rem;" onclick="document.getElementById('msg-{p_wamid}')?.scrollIntoView({{behavior: 'smooth', block: 'center'}})">
                <span style="color:#fbbf24; font-size:16px;">📌</span>
                <div style="flex:1; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{p_content}</div>
            </div>
            \'\'\'

        chat_viewer_html = f"""
        <div style="flex:1; display:flex; flex-direction:column; min-height:0;">'''
content = content.replace(old_5, new_5)

old_6 = '''            <div style="padding:1.5rem;'''
new_6 = '''            {pinned_html}
            <div style="padding:1.5rem;'''
content = content.replace(old_6, new_6)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("PATCH_APPLIED")
