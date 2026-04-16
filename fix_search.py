import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """    resultados = []
    # Usar dict para evitar iteraciones conflictivas
    for wa_id, session in list(sesiones.items()):
        historial = session.get("historial", [])
        nombre = session.get("nombre_cliente", wa_id)
        
        matches_en_chat = []
        # Inverso para los m\u00e1s recientes
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
                    "msg_id": msg.get("msg_id", "")
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
            
    return {"ok": True, "resultados": resultados}"""

new_block = """    resultados = []
    
    # Mapa inverso: wa_id_miembro -> info del grupo al que pertenece
    # Para que busquedas de miembros de grupo redirijan al grupo reflejo
    miembro_a_grupo = {}
    for vg in global_groups:
        for m in vg.get("members", []):
            miembro_a_grupo[m] = {"grupo_id": vg.get("id"), "grupo_nombre": vg.get("name", "Grupo")}

    # Usar dict para evitar iteraciones conflictivas
    for wa_id, session in list(sesiones.items()):
        historial = session.get("historial", [])
        nombre = session.get("nombre_cliente", wa_id)
        
        matches_en_chat = []
        # Inverso para los m\u00e1s recientes
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
                    "msg_id": msg.get("msg_id", "")
                })
                # Max 3 matches por chat para no saturar
                if len(matches_en_chat) >= 3:
                    break
        
        if matches_en_chat:
            # Si el wa_id es miembro de un grupo virtual, redirigir al grupo
            grupo_info = miembro_a_grupo.get(wa_id)
            if grupo_info:
                resultados.append({
                    "wa_id": grupo_info["grupo_id"],
                    "nombre": f"\\U0001f465 {grupo_info['grupo_nombre']}",
                    "nombre_real": nombre,
                    "wa_id_origen": wa_id,
                    "matches": matches_en_chat
                })
            else:
                resultados.append({
                    "wa_id": wa_id,
                    "nombre": nombre,
                    "matches": matches_en_chat
                })
            
    return {"ok": True, "resultados": resultados}"""

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("OK - Parche aplicado exitosamente")
else:
    print("ERROR - No se encontro el bloque a reemplazar")
    # Buscar la linea exacta para debug
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'resultados = []' in line:
            print(f"  Linea {i}: {repr(line)}")
