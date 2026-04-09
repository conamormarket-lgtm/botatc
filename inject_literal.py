import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. In renderizar_inbox (Line 1679 usually)
target1 = r"""            texto  = m["content"].replace("\\n", "<br>")
            
            # --- Renderizar media_id si es [sticker:ID] o [imagen:ID] ---
            import re"""

replacement1 = r"""            texto  = m["content"].replace("\\n", "<br>")
            
            # --- Renderizar números de teléfono clickeables ---
            import re
            def wrap_phone(match):
                phone = match.group(1)
                clean_phone = re.sub(r'[\s\-]', '', phone)
                # Solo si tiene más de 6 dígitos
                if sum(c.isdigit() for c in clean_phone) >= 7:
                    # Escape seguro
                    return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
                return phone
            texto = re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)

            # --- Renderizar media_id si es [sticker:ID] o [imagen:ID] ---"""

if target1 in text:
    text = text.replace(target1, replacement1)
    print("Replaced inside renderizar")
else:
    print("Failed to find target1")

# 2. Add /api/admin/chat/init endpoint
target2 = r"""@app.post("/api/admin/enviar_mensaje")
async def enviar_mensaje_api(request: Request):"""

replacement2 = r"""@app.post("/api/admin/chat/init")
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

@app.post("/api/admin/enviar_mensaje")
async def enviar_mensaje_api(request: Request):"""

if target2 in text:
    text = text.replace(target2, replacement2)
    print("Replaced init chat")
else:
    print("Failed to find target2")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
