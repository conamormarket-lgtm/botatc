import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# First occurrence (QR upload)
old_qr = '''        media_id = await subir_media(content, file.content_type, file.filename or "upload")
        if media_id:'''

new_qr = '''        media_id = await subir_media(content, file.content_type, file.filename or "upload")
        if media_id and not media_id.startswith("ERROR_META:"):'''
text = text.replace(old_qr, new_qr)

# Second occurrence (Admin upload media)
old_admin = '''        media_id = await subir_media(content, final_mime, file.filename or fallback_name)

        if media_id:
            return {"ok": True, "media_id": media_id, "tipo": "audio"}
        else:
            return {"ok": False, "error": "Error subiendo a WhatsApp. Puede que el formato sea inválido."}'''

new_admin = '''        media_id = await subir_media(content, final_mime, file.filename or fallback_name)

        if media_id and not media_id.startswith("ERROR_META:"):
            return {"ok": True, "media_id": media_id, "tipo": "audio"}
        else:
            err_msg = media_id.replace("ERROR_META:", "") if media_id else "Unknown Format"
            return {"ok": False, "error": f"Meta API Error: {err_msg}"}'''
text = text.replace(old_admin, new_admin)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated server.py to handle ERROR_META")
