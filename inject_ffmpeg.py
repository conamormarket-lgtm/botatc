import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_upload = '''@app.post("/api/admin/upload_media")
async def admin_upload_media(file: UploadFile = File(...)):
    """Sube media directamente desde la interfaz Web a Meta Graph."""
    try:
        from whatsapp_client import subir_media
        content = await file.read()
        
        fallback_name = "upload.bin"
        if file.content_type:
            if "image" in file.content_type: fallback_name = "upload.png"
            elif "video" in file.content_type: fallback_name = "upload.mp4"
            elif "audio" in file.content_type: fallback_name = "upload.ogg"

        media_id = await subir_media(content, file.content_type, file.filename or fallback_name)'''

new_upload = '''@app.post("/api/admin/upload_media")
async def admin_upload_media(file: UploadFile = File(...)):
    """Sube media directamente desde la interfaz Web a Meta Graph."""
    try:
        from whatsapp_client import subir_media
        content = await file.read()
        
        fallback_name = "upload.bin"
        final_mime = file.content_type or "application/octet-stream"
        
        if final_mime:
            if "image" in final_mime: fallback_name = "upload.png"
            elif "video" in final_mime: fallback_name = "upload.mp4"
            elif "audio" in final_mime: fallback_name = "upload.ogg"

        # Conversion nativa WebM -> OGG para WhatsApp Voice Notes
        if "webm" in final_mime.lower() or "audio" in final_mime.lower():
            import subprocess, os, tempfile
            try:
                # Usar tmp para cross-platform compatibility
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
                    tmp_in.write(content)
                    tmp_in_name = tmp_in.name
                tmp_out_name = tmp_in_name.replace(".webm", ".ogg")
                
                # Ejecutar FFMPEG (disponible via Aptfile en Railway)
                # WhatsApp RECOMIENDA audio/ogg; codecs=opus para notas de voz perfectas
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', tmp_in_name,
                    '-c:a', 'libopus', '-b:a', '32k',
                    '-vbr', 'on', '-compression_level', '10',
                    tmp_out_name
                ], capture_output=True)
                
                if result.returncode == 0 and os.path.exists(tmp_out_name):
                    with open(tmp_out_name, "rb") as f_out:
                        content = f_out.read()
                    final_mime = "audio/ogg; codecs=opus"
                    fallback_name = "voice_note.ogg"
                else:
                    print("FFMPEG fallback ignorado o error:", result.stderr.decode('utf-8', 'ignore'))
                    # Fallback si no hay ffmpeg: Meta API a veces acepta MP4 audio crudo
                    final_mime = "audio/mp4" 
                    fallback_name = "voice_note.mp4"
                    
                os.remove(tmp_in_name)
                if os.path.exists(tmp_out_name): os.remove(tmp_out_name)
            except Exception as ex:
                print(f"Error procesando audio con ffmpeg: {ex}")
                final_mime = "audio/mp4"

        media_id = await subir_media(content, final_mime, file.filename or fallback_name)'''

if 'import tempfile' not in text:
    text = text.replace(old_upload, new_upload)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected ffmpeg audio conversion")
