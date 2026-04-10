import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""@app.post("/api/admin/enviar_manual")
async def enviar_manual_endpoint(request: Request):"""

injection = r"""@app.post("/api/admin/enviar_media_manual")
async def enviar_media_manual_endpoint(request: Request, wa_id: str = Form(...), file: UploadFile = File(...)):
    if not verificar_sesion(request):
        raise HTTPException(status_code=403, detail="No autorizado")

    if wa_id not in sesiones:
        return {"ok": False, "error": "Chat no existe"}

    contents = await file.read()
    from whatsapp_client import subir_media, enviar_media
    import anyio
    
    media_id = await anyio.to_thread.run_sync(subir_media, contents, file.content_type, file.filename)
    if not media_id:
        return {"ok": False, "error": "Error comunicando con Meta para subir archivo"}
        
    tipo_msg = "document"
    if file.content_type.startswith("image/"): tipo_msg = "image"
    elif file.content_type.startswith("video/"): tipo_msg = "video"
    elif file.content_type.startswith("audio/"): tipo_msg = "audio"
    
    exito = await anyio.to_thread.run_sync(enviar_media, wa_id, tipo_msg, media_id)
    if exito:
        import time
        ts = int(time.time())
        txt_bot = f"[{tipo_msg}:{media_id}|{file.filename}]"
        sesiones[wa_id]["historial"].append({"role": "assistant", "content": txt_bot, "timestamp": ts, "status": "sent"})
        try: 
            from firebase_client import guardar_sesion_chat
            guardar_sesion_chat(wa_id, sesiones[wa_id])
        except: pass
        return {"ok": True}
    else:
        return {"ok": False, "error": "Error enviando vía Meta"}

@app.post("/api/admin/enviar_manual")
async def enviar_manual_endpoint(request: Request):"""

if target in text:
    text = text.replace(target, injection)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Endpoint injected successfully.")
else:
    print("Error: Target not found.")
