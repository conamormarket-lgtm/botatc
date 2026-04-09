import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

m = re.search(r'texto\s*=\s*m\[\"content\"\]\.replace\(\"\\n\", \"<br>\"\)', text)
if m:
    replacement = m.group(0) + r"""
            
            def wrap_phone(match):
                phone = match.group(1)
                clean_phone = re.sub(r'[\s\-]', '', phone)
                # Solo si tiene más de 6 dígitos
                if sum(c.isdigit() for c in clean_phone) >= 7:
                    # Escape seguro
                    return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
                return phone
            texto = re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)"""
    new_text = text.replace(m.group(0), replacement)
    
    # 2. Add /api/admin/chat/init endpoint before @app.post("/api/admin/enviar_mensaje")
    target2 = r'@app.post("/api/admin/enviar_mensaje")'
    replacement2 = r"""@app.post("/api/admin/chat/init")
async def init_chat(request: Request):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await request.json()
    wa_id = data.get("wa_id", "").replace("+", "").replace(" ", "")
    if len(wa_id) > 6 and wa_id not in sesiones:
        sesiones[wa_id] = {
            "historial": [],
            "datos_pedido": {},
            "bot_activo": False,
            "ultima_actividad": datetime.utcnow()
        }
    return {"ok": True}

@app.post("/api/admin/enviar_mensaje")"""
    new_text = new_text.replace(target2, replacement2)

    with open("server.py", "w", encoding="utf-8") as f:
        f.write(new_text)
    print("Injected into server.py successfully!")
else:
    print("Target 1 completely missing")
