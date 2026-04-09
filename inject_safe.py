with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Inject phone logic at lines 1389 and 1679
c1 = 'texto     = m["content"].replace("\\n", "<br>")'
if c1 in text:
    text = text.replace(c1, c1 + '''
        def wrap_phone(match):
            phone = match.group(1)
            clean_phone = __import__('re').sub(r'[\\s\\-]', '', phone)
            if sum(c.isdigit() for c in clean_phone) >= 7:
                return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \\'{clean_phone}\\')">{phone}</span>'
            return phone
        texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)''')

c2 = 'texto  = m["content"].replace("\\\\n", "<br>")'
if c2 in text:
    text = text.replace(c2, c2 + '''
            def wrap_phone2(match):
                phone = match.group(1)
                clean_phone = __import__('re').sub(r'[\\s\\-]', '', phone)
                if sum(c.isdigit() for c in clean_phone) >= 7:
                    return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \\'{clean_phone}\\')">{phone}</span>'
                return phone
            texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone2, texto)''')

# 2. Inject Document Support (Parser)
c3 = 'filename = mensaje_data.get("document", {}).get("filename", "archivo")'
c3_full = c3 + '\n            texto_cliente = f"[📎 Archivo: {filename}]"'
if c3_full in text:
    text = text.replace(c3_full, c3 + '\n            media_id = mensaje_data.get("document", {}).get("id", "")\n            texto_cliente = f"[documento:{media_id}|{filename}]"')

# 3. Inject Document Support (Renderer)
c4 = 'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video):([^\]]+)\]", reemplazar_archivos_inline, texto)'
if c4 in text:
    text = text.replace(c4, 'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video|documento):([^\]]+)\]", reemplazar_archivos_inline, texto)')

c5 = 'elif tipo == "audio":'
c5_full = c5 + '\n                    return f\'<div style="text-align:center;"><audio controls src="{src_url}" style="max-width: 250px; height: 40px; outline: none; margin-bottom: 5px;"></audio></div>\''
if c5_full in text:
    text = text.replace(c5_full, c5_full + '''
                elif tipo == "documento":
                    partes = media_id.split("|", 1)
                    doc_id = partes[0]
                    doc_name = partes[1] if len(partes) > 1 else "Documento"
                    doc_url = f"/api/media/{doc_id}"
                    return f'<div style="margin-bottom: 5px;"><a href="{doc_url}" download="{doc_name}" target="_blank" style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-decoration: none; color: inherit; font-size: 0.9rem; border: 1px solid var(--accent-border);">📎 {doc_name} <span style="font-size:0.8rem; margin-left:auto; opacity:0.6;">📥 Bajar</span></a></div>' ''')

# 4. Inject init_chat
c6 = '@app.post("/api/admin/enviar_mensaje")'
if c6 in text and 'init_chat' not in text:
    text = text.replace(c6, '''@app.post("/api/admin/chat/init")
async def init_chat(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id", "").replace("+", "").replace(" ", "")
    if len(wa_id) > 6 and wa_id not in sesiones:
        from datetime import datetime
        sesiones[wa_id] = {
            "historial": [],
            "datos_pedido": {},
            "bot_activo": False,
            "ultima_actividad": datetime.utcnow()
        }
    return {"ok": True}

@app.post("/api/admin/enviar_mensaje")''')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Safely replaced directly!")
