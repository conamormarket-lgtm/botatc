import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace get_media_endpoint
m1 = re.search(r'@app\.get\(\"/api/media/\{media_id\}\"\)\nasync def get_media_endpoint.*?return Response\(content=b\"\", status_code=404\)', text, flags=re.DOTALL)

replacement1 = """@app.get("/api/media/{media_id}")
async def get_media_endpoint(media_id: str):
    from fastapi.responses import Response, RedirectResponse
    if media_id in media_cache:
        data, mime = media_cache[media_id]
        return Response(content=data, media_type=mime)
        
    try:
        from whatsapp_client import obtener_media_url, descargar_media
        url = await obtener_media_url(media_id)
        if url:
            data, mime = await descargar_media(url)
            if data:
                media_cache[media_id] = (data, mime)
                return Response(content=data, media_type=mime)
    except: pass
    
    # DEVUELVE UN PLACEHOLDER NATIVO POR DEFAULT en vez de 404 para evitar parpadeos y errores de javascript en el cliente
    return RedirectResponse("https://placehold.co/250x150?text=Media+Expirado", status_code=302)"""

if m1:
    text = text.replace(m1.group(0), replacement1)
    
# Remove get_media_proxy block
m2 = re.search(r'@app\.get\(\"/api/media/\{media_id\}\"\)\nasync def get_media_proxy.*?return Response\(content=contenido, media_type=mime_type or "image/jpeg"\)\n\n', text, flags=re.DOTALL)
if m2:
    text = text.replace(m2.group(0), "")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fix applied successfully.")
