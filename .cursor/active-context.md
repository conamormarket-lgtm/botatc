> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `document_loader.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Prevenir — reduces excessive function call frequency**: -             try {
+             if (window.isSending) return;
-                 // Prevenir caché del navegador
+             try {
-                 const url = window.location.href;
+                 // Prevenir caché del navegador
-                 let fetchUrl = url + (url.includes('?') ? '&' : '?') + 't=' + new Date().getTime() + '&ajax=1';
+                 const url = window.location.href;
-                 // Si se cargó el historial completo (búsqueda de mensaje antiguo), mantenerlo en el polling
+                 let fetchUrl = url + (url.includes('?') ? '&' : '?') + 't=' + new Date().getTime() + '&ajax=1';
-                 if (window._viewingAllHistory) fetchUrl += '&history=all';
+                 // Si se cargó el historial completo (búsqueda de mensaje antiguo), mantenerlo en el polling
- 
+                 if (window._viewingAllHistory) fetchUrl += '&history=all';
-                 const res = await fetch(fetchUrl, {
+ 
-                     cache: 'no-store',
+                 const res = await fetch(fetchUrl, {
-                     headers: { 'Cache-Control': 'no-cache' }
+                     cache: 'no-store',
-                 });
+                     headers: { 'Cache-Control': 'no-cache' }
- 
+                 });
-                 const text = await res.text();
+ 
-                 const doc = new DOMParser().parseFromString(text, 'text/html');
+                 const text = await res.text();
- 
+                 const doc = new DOMParser().parseFromString(text, 'text/html');
-                 // Actualizar Lista de Conversaciones
+ 
-                 const newChats = doc.querySelector('.chats-container');
+                 // Actualizar Lista de Conversaciones
-                 const oldChats = document.querySelector('.chats-container');
+                 const newChats = doc.querySelector('.chats-container');
-                 if (newChats && oldChats && oldChats.innerHTML !== newChats.innerHTML) {
+
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **⚠️ GOTCHA: Patched security issue None — parallelizes async operations for speed**: -         import asyncio
+         from starlette.concurrency import run_in_threadpool
-         loop = asyncio.get_event_loop()
+         
-         
+         async def call_enviar_media(*args, **kwargs):
-         async def call_enviar_media(*args, **kwargs):
+             from functools import partial
-             return await loop.run_in_executor(None, lambda: enviar_media(*args, **kwargs))
+             return await run_in_threadpool(partial(enviar_media, *args, **kwargs))
-             return await loop.run_in_executor(None, lambda: enviar_mensaje(*args, **kwargs))
+             from functools import partial
-         partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
+             return await run_in_threadpool(partial(enviar_mensaje, *args, **kwargs))
-         last_wamid = None
+         partes = re.split(r'(\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\]]+\])', texto)
-         exito_alguna_parte = False
+         last_wamid = None
-         
+         exito_alguna_parte = False
-         for p in partes:
+         
-             p = p.strip()
+         for p in partes:
-             if not p: continue
+             p = p.strip()
-             
+             if not p: continue
-             match_sticker = re.match(r"^\[sticker:([^\|\]]+)\]$", p)
+             
-             match_img = re.match(r"^\[imagen:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
+             match_sticker = re.match(r"^\[sticker:([^\|\]]+)\]$", p)
-             match_video = re.match(r"^\[video:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
+             match_img = re.match(r"^\[imagen:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
-             match_audio = re.match(r"^\[audio:([^\|\]]+)\]$", p)
+             match_video = re.match(r"^\[video:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
-             match_doc = re.match(r"^\[documento:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
+             match_audio = re.match
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]

### 📐 Generic Logic Conventions & Fixes
- **[convention] Patched security issue False — protects against XSS and CSRF token theft — confirmed 3x**: -             procesar_mensaje_interno, numero_wa, nombre, texto_unido, False, last_id, numero_wa  # numero_wa aqui ES el session_key
+             procesar_mensaje_interno, numero_wa, nombre, texto_unido, False, last_id
- def procesar_mensaje_interno(numero_wa: str, nombre: str, texto_cliente: str, is_simulacion: bool = False, msg_id: str = None, session_key: str = None) -> str | None:
+ def procesar_mensaje_interno(numero_wa: str, nombre: str, texto_cliente: str, is_simulacion: bool = False, msg_id: str = None) -> str | None:
-     
+ 
-     # Usar session_key si fue pasado (para chats QR o multilínea con clave compuesta)
+     # ── Obtener/crear sesión ──────────────────────────────
-     # Si no, usar numero_wa como clave (comportamiento API clásico)
+     sesion = obtener_o_crear_sesion(numero_wa)
-     _skey = session_key or numero_wa
+     sesion["ultima_actividad"] = datetime.utcnow()
- 
+     sesion["nombre_cliente"]   = nombre
-     # ── Obtener/crear sesión ──────────────────────────────
+ 
-     sesion = obtener_o_crear_sesion(_skey)
+     # 1) Para simulaciones, guardamos el mensaje aquí. Para en vivo, recibir_mensaje ya lo guarda al instante.
-     sesion["ultima_actividad"] = datetime.utcnow()
+     if is_simulacion:
-     sesion["nombre_cliente"]   = nombre
+         if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
- 
+             import time
-     # 1) Para simulaciones, guardamos el mensaje aquí. Para en vivo, recibir_mensaje ya lo guarda al instante.
+             ts = int(time.time()) # fallback
-     if is_simulacion:
+             sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id, "timestamp": ts})
-         if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
+             
-             import time
+             try: 
-             ts = int(time.time()) # fallback
+                 from firebase_client import guardar_
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] Replaced dependency server**: -         try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
+         try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(_skey, sesion)
-     try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesion)
+     try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(_skey, sesion)

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[problem-fix] problem-fix in server.py**: -         print(f"  [👤 Humano -> {numero_envio} ({line_id})]: {texto}")
+         print(f"  [[OK] Humano -> {numero_envio} ({line_id})]: {texto}")

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[problem-fix] Fixed null crash in Sube — reduces excessive function call frequency**: - 
+             if (wa_id && wa_id !== "inbox") {
-             try {
+                 formData.append("wa_id", wa_id);
-                 // Sube el archivo de forma completamente asíncrona a nuestro servidor
+             }
-                 const uploadRes = await fetch('/api/admin/upload_media', {
+ 
-                     method: 'POST',
+             try {
-                     body: formData
+                 // Sube el archivo de forma completamente asíncrona a nuestro servidor
-                 });
+                 const uploadRes = await fetch('/api/admin/upload_media', {
- 
+                     method: 'POST',
-                 const uploadData = await uploadRes.json();
+                     body: formData
-                 if (!uploadData.ok) {
+                 });
-                     upObj.error = uploadData.error || 'Error subiendo';
+ 
-                     window.renderPendingMediaUI();
+                 const uploadData = await uploadRes.json();
-                     return;
+                 if (!uploadData.ok) {
-                 }
+                     upObj.error = uploadData.error || 'Error subiendo';
- 
+                     window.renderPendingMediaUI();
-                 upObj.media_id = uploadData.media_id;
+                     return;
-                 window.renderPendingMediaUI();
+                 }
-                 // Siempre queda en la cola — el usuario decide si agrega pie de imagen y presiona Enviar
+ 
- 
+                 upObj.media_id = uploadData.media_id;
-             } catch (e) {
+                 window.renderPendingMediaUI();
-                 console.error("Fallo de red al enviar media:", e);
+                 // Siempre queda en la cola — el usuario decide si agrega pie de imagen y presiona Enviar
-                 upObj.error = "Error red";
+ 
-                 window.renderPendingMediaUI();
+             } catch (e) {
-             }
+                 console.error
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] problem-fix in server.py — confirmed 3x**: -                         body: JSON.stringify({{ id, title, mensajes, delay_ms: delay, category: cat, type: "text", etiquetas, line_id: new URLSearchParams(window.location.search).get("line") || "principal" }})
+                         body: JSON.stringify({{ id, title, mensajes, delay_ms: delay, category: cat, type: "text", etiquetas, line_id: window.ACTIVE_CHAT_LINE || "principal" }})

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] Fixed null crash in PLANTILLAS — evolves the database schema to support new r... — confirmed 3x**: -             window.IS_QR_LINE = {_active_line_str.lower().startswith("qr_") | to_json};
+             window.IS_QR_LINE = {'true' if _active_line_str.lower().startswith('qr_') else 'false'};
-         </script>
+         // ================= PLANTILLAS LOGIC =================
-         """
+         async function cargarPlantillas() {{
- 
+             const list = document.getElementById("templateList");
-         chat_view_css = """
+             if (!list) return;
-         .bubble { max-width:85%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; word-wrap:break-word; overflow-wrap:anywhere; box-sizing:border-box; }
+             list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Cargando...</div>`;
-         .lado-izq { align-self:flex-start; }
+             try {{
-         .lado-der { align-self:flex-end; }
+                 const activeLine = window.ACTIVE_CHAT_LINE || "principal";
-         .bubble-bot { background:var(--primary-color); color:var(--text-main); border-bottom-right-radius:4px; }
+                 const res = await fetch("/api/admin/templates/list?line=" + activeLine);
-         .bubble-user { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
+                 const data = await res.json();
-         .bubble-sticker { background:transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }
+                 if (data.ok) {{
-         """
+                     list.innerHTML = "";
- 
+                     if (data.plantillas.length === 0) {{
-     # Reemplazos finales en la plantilla
+                         list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Sin plantillas. Apreta (+) para añadir.</div>`;
-     es_chat_valido = bool(wa_id and wa
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
