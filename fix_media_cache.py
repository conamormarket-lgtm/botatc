import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        media_id = await subir_media(content, final_mime, file.filename or fallback_name)
        
        if media_id:
            return {"ok": True, "media_id": media_id}"""

replacement = r"""        media_id = await subir_media(content, final_mime, file.filename or fallback_name)
        
        if media_id:
            # Meta no permite descargar media enviada por nosotros mismos.
            # Por lo que es de vital importancia guardarla en la cache para mostrarla en nuestro propio chat.
            media_cache[media_id] = (content, final_mime)
            return {"ok": True, "media_id": media_id}"""

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed Media Expirado issue!")
else:
    print("Target not found.")

