> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `document_loader.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Patched security issue Buscar — protects against XSS and CSRF token theft**: -     if not ses["historial"] or ses["historial"][-1].get("msg_id") != mensaje_id:
+     
-         import time
+     # Buscar si el mensaje ya existe (ej: placeholder CIPHERTEXT que luego se descifra)
-         ses["historial"].append({"role": "user", "content": texto_cliente, "msg_id": mensaje_id, "timestamp": int(time.time())})
+     msg_existente = next((m for m in reversed(ses["historial"][-20:]) if m.get("msg_id") == mensaje_id), None)
-         cur_unread = ses.get("unread_count", 0)
+     
-         ses["unread_count"] = 1 if cur_unread == -1 else cur_unread + 1
+     import time
-         try: 
+     if msg_existente:
-             from firebase_client import guardar_sesion_chat
+         # Si ya existe con este ID, actualizamos el contenido con el texto real
-             guardar_sesion_chat(session_key, ses)
+         msg_existente["content"] = texto_cliente
-         except: 
+     else:
-             pass
+         ses["historial"].append({"role": "user", "content": texto_cliente, "msg_id": mensaje_id, "timestamp": int(time.time())})
-     # -----------------------------------------------------------------------------------------
+         cur_unread = ses.get("unread_count", 0)
- 
+         ses["unread_count"] = 1 if cur_unread == -1 else cur_unread + 1
-     dict_msg = {"texto": texto_cliente, "id": mensaje_id}
+         
-     if session_key not in mensajes_pendientes:
+     try: 
-         mensajes_pendientes[session_key] = [dict_msg]
+         from firebase_client import guardar_sesion_chat
-         background_tasks.add_task(procesador_agregado, session_key, nombre)
+         guardar_sesion_chat(session_key, ses)
-     else:
+     except: 
-         mensajes_pendientes[session_key].append(dict_msg)
+         pass
- 
+     # -----------------------------------------------------------------------------------------
-     return {"status": "ok"}
+ 
- 
+     dict_msg = {"texto": texto_cliente, "id": mensaje_id}
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in Conjunto — parallelizes async operations for speed**: -     for num, s in todas:
+     # Conjunto para deduplicar por (linea_normalizada, numero_real) — evita mostrar
-         inactivo_horas = (ahora - s["ultima_actividad"]).total_seconds() / 3600
+     # sesiones corruptas con phone_number_id numérico de Meta junto a las correctas
-         activo = s.get("bot_activo", True)
+     _shown_combos = set()
-         is_archived = s.get("is_archived", False)
+ 
-         
+     for num, s in todas:
-         # Filtro de Tab
+         inactivo_horas = (ahora - s["ultima_actividad"]).total_seconds() / 3600
-         if tab == "archived":
+         activo = s.get("bot_activo", True)
-             if not is_archived: continue
+         is_archived = s.get("is_archived", False)
-         else:
+         
-             if is_archived: continue
+         # Filtro de Tab
-             if tab == "human" and activo:
+         if tab == "archived":
-                 continue
+             if not is_archived: continue
-             
+         else:
-         session_tags = s.get("etiquetas", [])
+             if is_archived: continue
-         if session_tags is None: session_tags = []
+             if tab == "human" and activo:
-         
+                 continue
-         # Filtro de Etiqueta (Label)
+             
-         if label_filter and label_filter not in session_tags:
+         session_tags = s.get("etiquetas", [])
-             continue
+         if session_tags is None: session_tags = []
-             
+         
-         # Filtro de No leídos (Verifica si el último mensaje lo envió el usuario)
+         # Filtro de Etiqueta (Label)
-         if is_unread:
+         if label_filter and label_filter not in session_tags:
-             hist_sin_sys = [m for m in s.get("historial", []) if m["role"] != "system"]
+             continue
-             if not hist_sin_sys or hist_sin_sys[-1]["role"] != "user":
+             
-                 continue
+         # Filtro de No l
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Patched security issue Para — protects against XSS and CSRF token theft**: -     Para la línea principal usamos solo el número (retrocompatible).
+     - Para la línea principal usamos solo el número (retrocompatible).
-     Para otras líneas usamos '{line_id}_{numero_wa}' para aislar conversaciones
+     - Para líneas QR (prefijo 'qr_') usamos '{line_id}_{numero_wa}'.
-     del mismo cliente en líneas distintas.
+     - Los phone_number_id numéricos de Meta son la línea principal.
-     return f"{line_id}_{numero_wa}"
+     # IDs numéricos son el phone_number_id real de Meta → línea principal
- 
+     if line_id.isdigit():
- 
+         return numero_wa
- def obtener_o_crear_sesion(numero_wa: str, line_id: str = "principal") -> dict:
+     # Solo las líneas con prefijo no-numérico (ej: qr_ventas_1) usan clave compuesta
-     """
+     return f"{line_id}_{numero_wa}"
-     Retorna la sesión existente si está dentro del tiempo válido,
+ 
-     la recupera de Firestore si el bot se reinició, o crea una nueva.
+ 
-     Usa clave compuesta line_id+numero para separar conversaciones por línea.
+ def obtener_o_crear_sesion(numero_wa: str, line_id: str = "principal") -> dict:
-     ahora = datetime.utcnow()
+     Retorna la sesión existente si está dentro del tiempo válido,
-     session_key = get_session_key(numero_wa, line_id)
+     la recupera de Firestore si el bot se reinició, o crea una nueva.
-     sesion = sesiones.get(session_key)
+     Usa clave compuesta line_id+numero para separar conversaciones por línea.
- 
+     """
-     if not sesion:
+     ahora = datetime.utcnow()
-         # 1. Intentar cargar desde Firebase si el servidor se reinició
+     session_key = get_session_key(numero_wa, line_id)
-         try:
+     sesion = sesiones.get(session_key)
-             from firebase_client import cargar_sesion_chat
+ 
-             sesion_db = cargar_sesion_chat(session_key)
+     if not sesion:
-             if sesion_db:
+         # 1. Intentar cargar desde Firebase si el servidor se reinició
- 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in True — parallelizes async operations for speed**: -         nombre_chat = s.get("nombre_cliente", wa_id)
+         nombre_chat = s.get("nombre_cliente", s.get("numero_real", wa_id))
-         activo_chat = s.get("bot_activo", True)
+         numero_chat_display = s.get("numero_real", wa_id)  # número real sin prefijo de línea
-         all_msgs = [m for m in s.get("historial", []) if m["role"] != "system"]
+         activo_chat = s.get("bot_activo", True)
-         
+         all_msgs = [m for m in s.get("historial", []) if m["role"] != "system"]
-         load_all = request.query_params.get("history") == "all" or bool(request.query_params.get("msg_id"))
+         
-         MAX_MENSAJES = 70
+         load_all = request.query_params.get("history") == "all" or bool(request.query_params.get("msg_id"))
-         msgs = all_msgs if load_all else all_msgs[-MAX_MENSAJES:]
+         MAX_MENSAJES = 70
-         
+         msgs = all_msgs if load_all else all_msgs[-MAX_MENSAJES:]
-         import re
+         
-         burbujas = ""
+         import re
-         pinned_messages = []
+         burbujas = ""
-         starred_messages = []
+         pinned_messages = []
-         if len(all_msgs) > MAX_MENSAJES and not load_all:
+         starred_messages = []
-             burbujas = f'<div style="text-align:center; opacity:0.8; margin: 1rem 0; font-size:0.8rem; background:var(--accent-bg); padding:0.6rem; border-radius:8px; border:1px solid var(--accent-border);">Mostrando últimos {MAX_MENSAJES} de {len(all_msgs)} mensajes.<br><button type="button" onclick="window.location.href = window.location.href + (window.location.href.includes(\'?\') ? \'&\' : \'?\') + \'history=all\';" style="background:var(--primary-color);color:white;border:none;padding:0.3rem 0.8rem;border-radius:6px;font-weight:600;cursor:pointer;margin-top:0.4rem;transition:background 0.2s;">📥 Cargar historial completo ([WARN] Más lento)</button></div>'
+         if len(all_msgs) > MAX_MENSAJES and not load_all:
-         last_date
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in Para — parallelizes async operations for speed**: -         nombre   = s.get("nombre_cliente", num)
+         # Para claves compuestas (line_id_numero), extraer el número real para mostrar
-         if not nombre: nombre = num
+         numero_display = s.get("numero_real", num)
-         preview  = ultimo_msg(s)
+         nombre   = s.get("nombre_cliente", numero_display)
-         time_str = tiempo_relativo(s["ultima_actividad"])
+         if not nombre: nombre = numero_display
-         
+         preview  = ultimo_msg(s)
-         is_vg = s.get("is_virtual_group", False)
+         time_str = tiempo_relativo(s["ultima_actividad"])
-         if is_vg:
+         
-             badge_html = '<span class="badge" style="background:rgba(168, 85, 247, 0.15); color:#a855f7; border: 1px solid rgba(168, 85, 247, 0.3);">👥 GRUPO VIRTUAL</span>'
+         is_vg = s.get("is_virtual_group", False)
-         else:
+         if is_vg:
-             badge_html = '<span class="badge">🟢 Bot Activo</span>'
+             badge_html = '<span class="badge" style="background:rgba(168, 85, 247, 0.15); color:#a855f7; border: 1px solid rgba(168, 85, 247, 0.3);">👥 GRUPO VIRTUAL</span>'
-             if not activo:
+         else:
-                 badge_html = '<span class="badge badge-alert">🔴 Esperando</span>'
+             badge_html = '<span class="badge">🟢 Bot Activo</span>'
-             
+             if not activo:
-         active_class = "active-row" if wa_id == num else ""
+                 badge_html = '<span class="badge badge-alert">🔴 Esperando</span>'
-         tags_html = ""
+         active_class = "active-row" if wa_id == num else ""
-         if session_tags:
+             
-             tags_html = '<div style="display:flex; gap:0.3rem; margin-top:0.3rem; flex-wrap:wrap;">'
+         tags_html = ""
-             for tid in session_tags:
+         if session_tags:
-                 lbl = next((l for l in global_labels if l.get("id") == tid), None)
+             tags_html = '<div 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Patched security issue Webhook — protects against XSS and CSRF token theft**: -     ses = obtener_o_crear_sesion(numero_wa)
+     session_key = get_session_key(numero_wa, phone_number_id)
-     ses["ultima_actividad"] = datetime.utcnow()
+     ses = obtener_o_crear_sesion(numero_wa, phone_number_id)
-     ses["nombre_cliente"]   = nombre
+     ses["ultima_actividad"] = datetime.utcnow()
-     ses["lineId"]           = phone_number_id
+     ses["nombre_cliente"]   = nombre
-     if not ses["historial"] or ses["historial"][-1].get("msg_id") != mensaje_id:
+     ses["lineId"]           = phone_number_id
-         import time
+     ses["numero_real"]      = numero_wa
-         ses["historial"].append({"role": "user", "content": texto_cliente, "msg_id": mensaje_id, "timestamp": int(time.time())})
+     if not ses["historial"] or ses["historial"][-1].get("msg_id") != mensaje_id:
-         cur_unread = ses.get("unread_count", 0)
+         import time
-         ses["unread_count"] = 1 if cur_unread == -1 else cur_unread + 1
+         ses["historial"].append({"role": "user", "content": texto_cliente, "msg_id": mensaje_id, "timestamp": int(time.time())})
-         try: 
+         cur_unread = ses.get("unread_count", 0)
-             from firebase_client import guardar_sesion_chat
+         ses["unread_count"] = 1 if cur_unread == -1 else cur_unread + 1
-             guardar_sesion_chat(numero_wa, ses)
+         try: 
-         except: 
+             from firebase_client import guardar_sesion_chat
-             pass
+             guardar_sesion_chat(session_key, ses)
-     # -----------------------------------------------------------------------------------------
+         except: 
- 
+             pass
-     dict_msg = {"texto": texto_cliente, "id": mensaje_id}
+     # -----------------------------------------------------------------------------------------
-     if numero_wa not in mensajes_pendientes:
+ 
-         mensajes_pendientes[numero_wa] = [dict_msg]
+     dict_msg = {"texto": texto_cliente, "id": mensaje_i
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Added JWT tokens authentication — evolves the database schema to support new ...**: -     from bot_manager import get_bot_for_line
+     try:
-     lines_rich = {}
+         from server import get_qr_status
-     for lid, linfo in aliases.items():
+         qr_status = get_qr_status()
-         if isinstance(linfo, str):
+         if qr_status.get("connected"):
-             linfo = {"name": linfo}  # Migration from old string format
+             qr_line_id = qr_status.get("lineId", "qr_ventas_1")
-             
+             if qr_line_id not in aliases:
-         lname = linfo.get("name", "undefined")
+                 aliases[qr_line_id] = {"name": "Bot Ventas (Baileys Web)", "provider": "baileys"}
-         provider = linfo.get("provider", "meta" if lid == "principal" else "")
+     except Exception as e:
-         meta_phone_id = linfo.get("meta_phone_id", "")
+         pass
-         meta_token_has_value = bool(linfo.get("meta_token"))
+         
-         
+     from bot_manager import get_bot_for_line
-         lines_rich[lid] = {
+     lines_rich = {}
-             "name": lname,
+     for lid, linfo in aliases.items():
-             "provider": provider,
+         if isinstance(linfo, str):
-             "meta_phone_id": meta_phone_id,
+             linfo = {"name": linfo}  # Migration from old string format
-             "has_meta_token": meta_token_has_value, # Nunca devolver el token crudo a la UI por seguridad
+             
-             "bot_id": get_bot_for_line(lid)
+         lname = linfo.get("name", "undefined")
-         }
+         provider = linfo.get("provider", "meta" if lid == "principal" else "")
-         
+         meta_phone_id = linfo.get("meta_phone_id", "")
-     return {"ok": True, "lines": lines_rich}
+         meta_token_has_value = bool(linfo.get("meta_token"))
- 
+         
- @app.post("/api/admin/lines")
+         lines_rich[lid] = {
- async def api_save_line(payload: LineAliasPayload, request: Request):
+             "name": lname,
-     if not verificar_sesion(r
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Added JWT tokens authentication — evolves the database schema to support new ...**: - 
+     line_id: str = "principal"
- @app.post("/api/admin/templates/save")
+ 
- async def api_save_template(payload: TemplatePayload, request: Request):
+ @app.post("/api/admin/templates/save")
-     if not verificar_sesion(request):
+ async def api_save_template(payload: TemplatePayload, request: Request):
-         raise HTTPException(status_code=403, detail="No autorizado")
+     if not verificar_sesion(request):
-     from firebase_client import guardar_plantilla_bd
+         raise HTTPException(status_code=403, detail="No autorizado")
-     guardar_plantilla_bd(payload.name, payload.language)
+     from firebase_client import guardar_plantilla_bd
-     return {"ok": True}
+     guardar_plantilla_bd(payload.name, payload.language, payload.line_id)
- 
+     return {"ok": True}
- @app.post("/api/admin/templates/delete")
+ 
- async def api_delete_template(payload: TemplatePayload, request: Request):
+ @app.post("/api/admin/templates/delete")
-     if not verificar_sesion(request):
+ async def api_delete_template(payload: TemplatePayload, request: Request):
-         raise HTTPException(status_code=403, detail="No autorizado")
+     if not verificar_sesion(request):
-     from firebase_client import eliminar_plantilla_bd
+         raise HTTPException(status_code=403, detail="No autorizado")
-     eliminar_plantilla_bd(payload.name)
+     from firebase_client import eliminar_plantilla_bd
-     return {"ok": True}
+     eliminar_plantilla_bd(payload.name)
- 
+     return {"ok": True}
- @app.get("/api/admin/templates/list")
+ 
- async def api_list_templates(request: Request):
+ @app.get("/api/admin/templates/list")
-     if not verificar_sesion(request):
+ async def api_list_templates(request: Request):
-         raise HTTPException(status_code=403, detail="No autorizado")
+     if not verificar_sesion(request):
-     from firebase_client import cargar_plantillas_bd
+         raise HTTPException(status_code=403, detail="No a
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in False — evolves the database schema to support new requir...**: -             "pedido_id": s.get("datos_pedido", {}).get("id") if s.get("datos_pedido") else None,
+             "lineId": s.get("lineId"),
-             "estado_pedido": s.get("datos_pedido", {}).get("estadoGeneral") if s.get("datos_pedido") else None,
+             "numero_real": s.get("numero_real"),
-             "mensajes": historial_resumido,
+             "is_archived": s.get("is_archived", False),
-         }
+             "pedido_id": s.get("datos_pedido", {}).get("id") if s.get("datos_pedido") else None,
-     return resultado
+         }
- 
+     return resultado
- # ─────────────────────────────────────────────
+ 
- #  Simulador Web de Chat
+ # ─────────────────────────────────────────────
- # ─────────────────────────────────────────────
+ #  Simulador Web de Chat
- 
+ # ─────────────────────────────────────────────
- @app.get("/simulador", response_class=HTMLResponse)
+ 
- async def pagina_simulador(request: Request):
+ @app.get("/simulador", response_class=HTMLResponse)
-     """Interfaz web para probar el comportamiento del bot."""
+ async def pagina_simulador(request: Request):
-     if not verificar_sesion(request):
+     """Interfaz web para probar el comportamiento del bot."""
-         return RedirectResponse(url=f"/admin", status_code=302)
+     if not verificar_sesion(request):
-     return HTMLResponse("""
+         return RedirectResponse(url=f"/admin", status_code=302)
-     <html>
+     return HTMLResponse("""
-     <head>
+     <html>
-       <title>Simulador de WhatsApp</title>
+     <head>
-       <meta name="viewport" content="width=device-width,initial-scale=1">
+       <title>Simulador de WhatsApp</title>
-       <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
+       <meta name="viewport" content="width=device-width,initial-scale=1">
-       <style>
+       <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[problem-fix] problem-fix in server.py**: -         if qr_status.get("connected"):
+         if qr_status.get("status") == "connected":

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] what-changed in inbox.html**: -                     body: JSON.stringify({ name: name.trim(), language: lang.trim() })
+                     body: JSON.stringify({ name: name.trim(), language: lang.trim(), line_id: new URLSearchParams(window.location.search).get("line") || "principal" })

📌 IDE AST Context: Modified symbols likely include [html]
- **[discovery] discovery in server.py**: - async def api_list_templates(request: Request):
+ async def api_list_templates(request: Request, line_id: str = None):
-     plantillas = cargar_plantillas_bd()
+     plantillas = cargar_plantillas_bd(line_id)

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] problem-fix in server.py — confirmed 4x**: - def get_quick_replies(request: Request):
+ def get_quick_replies(request: Request, line: str = None):
-     return cargar_quick_replies_bd()
+     return cargar_quick_replies_bd(line)

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] what-changed in server_bad2.py**: File updated (external): server_bad2.py

Content summary (5030 lines):
��#
- **[convention] Fixed null crash in POST — prevents null/undefined runtime crashes — confirmed 3x**: -                 const urlParams = new URLSearchParams(window.location.search);
+                 const res = await fetch("/api/admin/templates/save", {
-                 const currentLine = urlParams.get("line") || "principal";
+                     method: "POST",
-                 const res = await fetch("/api/admin/templates/save", {
+                     headers: { "Content-Type": "application/json" },
-                     method: "POST",
+                     body: JSON.stringify({ name: name.trim(), language: lang.trim() })
-                     headers: { "Content-Type": "application/json" },
+                 });
-                     body: JSON.stringify({ name: name.trim(), language: lang.trim(), line_id: currentLine })
+                 if (res.ok) cargarPlantillas();
-                 });
+             } catch (e) {
-                 if (res.ok) cargarPlantillas();
+                 alert("Error guardando plantilla");
-             } catch (e) {
+             }
-                 alert("Error guardando plantilla");
+         }
-             }
+ 
-         }
+         async function eliminarPlantilla(name) {
- 
+             if (!confirm(`¿Borrar la plantilla '${name}' de tu lista local?`)) return;
-         async function eliminarPlantilla(name) {
+             try {
-             if (!confirm(`¿Borrar la plantilla '${name}' de tu lista local?`)) return;
+                 const res = await fetch("/api/admin/templates/delete", {
-             try {
+                     method: "POST",
-                 const res = await fetch("/api/admin/templates/delete", {
+                     headers: { "Content-Type": "application/json" },
-                     method: "POST",
+                     body: JSON.stringify({ name: name })
-                     headers: { "Content-Type": "application/json" },
+                 });
-                     body: JSON.stringify({ name: name })
+                 if (res.ok) cargarPlanti
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
