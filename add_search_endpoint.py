import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

endpoint = '''
@app.get("/api/admin/buscar_mensajes")
async def buscar_mensajes(q: str, request: Request):
    if not verificar_sesion(request):
        return {"ok": False, "error": "No autorizado"}
    
    q = q.lower().strip()
    if not q or len(q) < 2:
        return {"ok": True, "resultados": []}
    
    resultados = []
    # Usar dict para evitar iteraciones conflictivas
    for wa_id, session in list(sesiones.items()):
        historial = session.get("historial", [])
        nombre = session.get("nombre_cliente", wa_id)
        
        matches_en_chat = []
        # Inverso para los más recientes
        for msg in reversed(historial):
            content = msg.get("content", "")
            if content and q in content.lower() and msg.get("role") != "system":
                idx = content.lower().find(q)
                start = max(0, idx - 25)
                end = min(len(content), idx + len(q) + 25)
                snippet = content[start:end].replace("\\n", " ")
                if start > 0: snippet = "..." + snippet
                if end < len(content): snippet += "..."
                
                matches_en_chat.append({
                    "role": msg.get("role"),
                    "snippet": snippet,
                    "wamid": msg.get("wamid", "")
                })
                # Max 3 matches por chat para no saturar
                if len(matches_en_chat) >= 3:
                    break
        
        if matches_en_chat:
            resultados.append({
                "wa_id": wa_id,
                "nombre": nombre,
                "matches": matches_en_chat
            })
            
    return {"ok": True, "resultados": resultados}
'''

if 'def buscar_mensajes(' not in text:
    old_target = '@app.post("/api/admin/enviar_manual")'
    text = text.replace(old_target, endpoint + '\n' + old_target)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected backend search endpoint")
