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

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] Replaced auth JSON**: - const axios = require("axios");
+ const http = require("http");
- axios.post("http://127.0.0.1:3000/api/qr/pair", { telefono: telefono })
+ const data = JSON.stringify({ telefono: telefono });
-     .then(res => {
+ 
-         console.log(`
+ const options = {
- ===========[REDACTED]
+     hostname: '127.0.0.1',
- 🔥🔥 TU CÓDIGO DE WHATSAPP ES:  ${res.data.code}  🔥🔥
+     port: 3000,
- ===========[REDACTED]
+     path: '/api/qr/pair',
- 
+     method: 'POST',
- 1. Abre WhatsApp en tu celular.
+     headers: {
- 2. Toca los tres puntos (Menú) -> Dispositivos vinculados.
+         'Content-Type': 'application/json',
- 3. Toca "Vincular dispositivo".
+         'Content-Length': data.length
- 4. En la parte de abajo de la cámara, toca "Vincular con el número de teléfono".
+     }
- 5. ¡Ingresa este código!
+ };
-         `);
+ 
-     })
+ const req = http.request(options, res => {
-     .catch(err => {
+     let responseBody = '';
-         if (err.response) {
+     res.on('data', chunk => { responseBody += chunk; });
-             console.log(`❌ Error del servidor: ${err.response.data.error || JSON.stringify(err.response.data)}`);
+     
-             if (err.response.data.error && err.response.data.error.includes("Ya estás conectado")) {
+     res.on('end', () => {
-                 console.log("\n⚠️ Tienes que borrar la sesión actual. Ejecuta:");
+         try {
-                 console.log("pm2 stop bot-qr");
+             const parsed = JSON.parse(responseBody);
-                 console.log("rm -rf qr_service/auth_info_baileys");
+             if (res.statusCode >= 400) {
-                 console.log("pm2 start bot-qr\n");
+                 console.log(`❌ Error del servidor: ${parsed.error || responseBody}`);
-             }
+                 if (parsed.error && parsed.error.includes("Ya estás conectado")) {
-         } else {
+                     console.log("\n⚠️ Tienes que borrar la sesión actua
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [http, telefono, data, options, req]
- **[problem-fix] problem-fix in server.py**: -             model="gemini-2.5-flash-lite",
+             model="gemini-2.0-flash",

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
