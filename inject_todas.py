import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """    todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)
    lista_chats_html = ""
    
    # ------------------ Generador de Filtro de Etiquetas HTML ------------------"""

rep = """    grupos_sesiones = []
    for vg in global_groups:
        miembros = vg.get("members", [])
        sesiones_miembros = [sesiones.get(m) for m in miembros if m in sesiones]
        if not sesiones_miembros: continue
        vg_ultima_actividad = max((s.get("ultima_actividad", datetime.utcnow()) for s in sesiones_miembros))
        
        hist_total = []
        for s in sesiones_miembros:
            hist_total.extend(s.get("historial", []))
        hist_total.sort(key=lambda x: x.get("timestamp", ""))
        
        s_fake = {
            "ultima_actividad": vg_ultima_actividad,
            "nombre_cliente": f"{vg.get('name')}",
            "bot_activo": True,
            "historial": hist_total[-5:],
            "is_virtual_group": True,
            "vg_id": vg.get("id"),
            "etiquetas": []
        }
        grupos_sesiones.append((vg.get("id"), s_fake))

    todas = sorted(list(sesiones.items()) + grupos_sesiones, key=lambda x: x[1].get("ultima_actividad", datetime.min), reverse=True)
    lista_chats_html = ""
    
    # ------------------ Generador de Filtro de Etiquetas HTML ------------------"""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected todas generation.")
else:
    print("Target not found.")

