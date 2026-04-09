> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Request — parallelizes async operations for speed**: - @app.post("/api/admin/enviar_manual")
+ 
- async def enviar_manual_endpoint(request: Request):
+ @app.get("/api/admin/buscar_mensajes")
-     """Recibe mensaje del panel web y lo despacha a WhatsApp nativamente."""
+ async def buscar_mensajes(q: str, request: Request):
-         raise HTTPException(status_code=403, detail="No autorizado")
+         return {"ok": False, "error": "No autorizado"}
-     data = await request.json()
+     q = q.lower().strip()
-     wa_id = data.get("wa_id")
+     if not q or len(q) < 2:
-     texto = data.get("texto", "").strip()
+         return {"ok": True, "resultados": []}
-     reply_to_wamid = data.get("reply_to_wamid")
+     
-     
+     resultados = []
-     if not wa_id or wa_id not in sesiones or not texto:
+     # Usar dict para evitar iteraciones conflictivas
-         return {"ok": False}
+     for wa_id, session in list(sesiones.items()):
-         
+         historial = session.get("historial", [])
-     s = sesiones[wa_id]
+         nombre = session.get("nombre_cliente", wa_id)
-     # No guardamos en historial todavía, hasta confirmar envío
+         
-     
+         matches_en_chat = []
-     from whatsapp_client import enviar_mensaje, enviar_media
+         # Inverso para los más recientes
-     import re
+         for msg in reversed(historial):
-     
+             content = msg.get("content", "")
-     async def process_and_send():
+             if content and q in content.lower() and msg.get("role") != "system":
-         from whatsapp_client import enviar_media, enviar_mensaje, subir_media
+                 idx = content.lower().find(q)
-         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\]|\[video:[^\]]+\]|\[audio:[^\]]+\]|\[sticker-local:[^\]]+\])', texto)
+                 start = max(0, idx - 25)
-         last_wamid = None
+                 end = min(len(content), idx + len(q) + 25)
-         exito_alguna_parte = False
+                 snippet = 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]

### 📐 Generic Logic Conventions & Fixes
- **[convention] Fixed null crash in Sticker — prevents null/undefined runtime crashes — confirmed 3x**: -                 // Check if it's a sticker
+                 let clickedImg = e.target.closest('img');
-                 let stickerImg = bubble.querySelector('img[alt^="Sticker"]');
+                 let stickerImg = null;
-                 let ctxSaveSticker = document.getElementById("ctxSaveSticker");
+                 let regularImg = null;
-                 if (stickerImg) {
+ 
-                     ctxTargetMediaId = stickerImg.getAttribute('alt').replace('Sticker ', '').trim();
+                 if (clickedImg && clickedImg.getAttribute('alt')) {
-                     ctxSaveSticker.style.display = 'flex';
+                     if (clickedImg.getAttribute('alt').startsWith("Sticker")) {
-                 } else {
+                         stickerImg = clickedImg;
-                     ctxTargetMediaId = "";
+                     } else if (clickedImg.getAttribute('alt').startsWith("Imagen")) {
-                     ctxSaveSticker.style.display = 'none';
+                         regularImg = clickedImg;
-                 }
+                     }
- 
+                 } else {
-                 let regularImg = bubble.querySelector('img[alt^="Imagen"]');
+                     stickerImg = bubble.querySelector('img[alt^="Sticker"]');
-                 let ctxCopyImage = document.getElementById("ctxCopyImage");
+                     regularImg = bubble.querySelector('img[alt^="Imagen"]');
-                 let ctxDownloadImage = document.getElementById("ctxDownloadImage");
+                 }
-                 if (regularImg && !stickerImg) {
+ 
-                     ctxTargetImageUrl = regularImg.src;
+                 let ctxSaveSticker = document.getElementById("ctxSaveSticker");
-                     ctxCopyImage.style.display = 'flex';
+                 if (stickerImg) {
-                     ctxDownloadImage.style.display = 'flex';
+                     ctxTargetMediaId = stickerImg.getAttribute('alt').replace('Sticker 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in inbox.html**: -                                             div.className = 'bubble bubble-out';
+                                             div.className = 'bubble bubble-bot lado-der';

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 3x**: -                 bubble.className = "bubble bubble-bot lado-izq";
+                 bubble.className = "bubble bubble-bot lado-der";

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in WhatsApp — prevents null/undefined runtime crashes — confirmed 4x**: -                                         alert("El servidor de WhatsApp (Meta) rechazó o no pudo procesar el formato del audio.");
+                                         alert("El servidor de WhatsApp (Meta) rechazó o no pudo procesar el formato del audio.\n\nDetalle técnico: " + (enviaRes?.error || "Desconocido"));

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Audio — fixes memory leak from uncleared timers — confirmed 3x**: -                         alert("Es necesario otorgar permisos de micrófono al navegador para grabar audios.");
+                         console.error('Audio Recorder Error:', err);
-                     }
+                         if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
-                 } else {
+                             alert("❌ ¡Conexión Insegura! Tu navegador ha bloqueado el micrófono por seguridad. Las web de grabación de audio OBLIGAN a que uses 'https://' o entres desde 'http://localhost' en lugar de usar una IP directa de la red.");
-                     // Stop recording (this triggers the "stop" event listener above to send the message)
+                         } else {
-                     mediaRecorder.stop();
+                             alert("Permiso Denegado o Error: " + err.message + ". Verifica el candadito arriba a la izquierda y dale permisos al micrófono.");
-                     isRecording = false;
+                         }
-                     mediaRecorder.stream.getTracks().forEach(t => t.stop());
+                     }
-                     
+                 } else {
-                     btnRecord.style.background = "var(--accent-bg)";
+                     // Stop recording (this triggers the "stop" event listener above to send the message)
-                     btnRecord.style.color = "var(--text-main)";
+                     mediaRecorder.stop();
-                     btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
+                     isRecording = false;
-                     
+                     mediaRecorder.stream.getTracks().forEach(
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Wait — confirmed 4x**: -         document.getElementById('chatSearchInput')?.addEventListener('input', window.aplicarFiltroChats);
+         
- 
+         const searchInp = document.getElementById('chatSearchInput');
-         function iniciarNuevoChat() {
+         if (searchInp) {
-             let val = document.getElementById('chatSearchInput').value.trim();
+             const savedSearch = sessionStorage.getItem('chatSearchValue');
-             val = val.replace(/\D/g, ''); // purgar caracteres no numéricos
+             if (savedSearch) {
-             if (val.length < 9) return alert("Número muy corto");
+                 searchInp.value = savedSearch;
-             if (!val.startsWith("51")) val = "51" + val;
+                 // Wait for DOM to finish then apply
-             window.location.href = `/inbox/${val}`;
+                 setTimeout(() => { if(window.aplicarFiltroChats) window.aplicarFiltroChats(); }, 100);
-         }
+             }
- 
+             
-         // EMOJI PICKER HOOK - Global event delegation
+             searchInp.addEventListener('input', function(e) {
-         document.addEventListener('emoji-click', event => {
+                 sessionStorage.setItem('chatSearchValue', this.value);
-             const input = document.getElementById('manualMsgInput');
+                 if(window.aplicarFiltroChats) window.aplicarFiltroChats();
-             if (input) {
+             });
-                 input.value += event.detail.unicode;
+         }
-                 input.focus();
+ 
-             }
+ 
-         });
+         function iniciarNuevoChat() {
- 
+             let val = document.getElementById('chatSearchInput').value.trim();
-         // CERRAR MENÚS FLOTANTES AL HACER CLICK AFUERA
+             val = val.replace(/\D/g, ''); // purgar caracteres no numéricos
-         document.addEventListener("click", function (e) {
+             if (val.length < 9) return alert("Número muy corto");
-             const
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] Replaced dependency MODO**: -         # Solo lo agregamos si no está ya como último mensaje (evitar duplicados lógicos)
+ 
-         if not sesion["historial"] or sesion["historial"][-1].get("content") != texto_cliente:
+ 
-             sesion["historial"].append({"role": "user", "content": texto_cliente})
+         # ── MODO TESTER: preguntar N° de pedido manualmente ──
- 
+         if es_tester:
-         # ── MODO TESTER: preguntar N° de pedido manualmente ──
+             # Si ya nos dijo el número de pedido, buscarlo por ID
-         if es_tester:
+             if sesion.get("esperando_pedido_tester"):
-             # Si ya nos dijo el número de pedido, buscarlo por ID
+                 from firebase_client import inicializar_firebase
-             if sesion.get("esperando_pedido_tester"):
+                 db = inicializar_firebase()
-                 from firebase_client import inicializar_firebase
+                 id_pedido = texto_cliente.strip().upper()
-                 db = inicializar_firebase()
+                 try:
-                 id_pedido = texto_cliente.strip().upper()
+                     doc = db.collection("pedidos").document(id_pedido).get()
-                 try:
+                     datos = doc.to_dict() if doc.exists else None
-                     doc = db.collection("pedidos").document(id_pedido).get()
+                 except Exception:
-                     datos = doc.to_dict() if doc.exists else None
+                     datos = None
-                 except Exception:
+ 
-                     datos = None
+                 if datos:
- 
+                     sesion["esperando_pedido_tester"] = False
-                 if datos:
+                     sesion["datos_pedido"] = datos
-                     sesion["esperando_pedido_tester"] = False
+                     sesion["nombre_cliente"] = f"{datos.get('clienteNombre','')} {datos.get('clienteApellidos','')}".strip() or nombre
-                     sesion["datos_pedido"
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in Obtener — protects against XSS and CSRF token theft — confirmed 4x**: -     global BOT_GLOBAL_ACTIVO
+ 
-     if not BOT_GLOBAL_ACTIVO:
+     # ── Obtener/crear sesión ──────────────────────────────
-         print(f"  [⏹ Bot APAGADO globalmente → silencio]")
+     sesion = obtener_o_crear_sesion(numero_wa)
-         return None
+     sesion["ultima_actividad"] = datetime.utcnow()
- 
+     sesion["nombre_cliente"]   = nombre
-     # ── Obtener/crear sesión ──────────────────────────────
+ 
-     sesion = obtener_o_crear_sesion(numero_wa)
+     # 1) Guardar mensaje TEMPRANO para que SIEMPRE aparezca en el Inbox, sin duplicarse
-     sesion["ultima_actividad"] = datetime.utcnow()
+     if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
-     sesion["nombre_cliente"]   = nombre
+         sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id})
- 
+         # ¡GUARDADO INMEDIATO PARA EVITAR PERDIDA ANTES DE LOS RETORNOS TEMPRANOS!
-     # 1) Guardar mensaje TEMPRANO para que SIEMPRE aparezca en el Inbox, sin duplicarse
+         try: 
-     if not sesion["historial"] or sesion["historial"][-1].get("msg_id") != msg_id:
+             from firebase_client import guardar_sesion_chat
-         sesion["historial"].append({"role": "user", "content": texto_cliente, "msg_id": msg_id})
+             guardar_sesion_chat(numero_wa, sesion)
-         # ¡GUARDADO INMEDIATO PARA EVITAR PERDIDA ANTES DE LOS RETORNOS TEMPRANOS!
+         except Exception as e:
-         try: 
+             print(f"  [⚠️ Error guardando sesión temprana: {e}]")
-             from firebase_client import guardar_sesion_chat
+ 
-             guardar_sesion_chat(numero_wa, sesion)
+     global BOT_GLOBAL_ACTIVO
-         except Exception as e:
+     if not BOT_GLOBAL_ACTIVO:
-             print(f"  [⚠️ Error guardando sesión temprana: {e}]")
+         print(f"  [⏹ Bot APAGADO globalmente → silencio (guardado en BD)]")
- 
+         return None
-     # ── Buscar pedido en Firebase 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[what-changed] Updated schema Conversion**: - old_code = """        # Conversion nativa WebM -> OGG para WhatsApp Voice Notes
+ new_block = """# Conversion nativa WebM -> MP4 para WhatsApp Voice Notes
-         if "webm" in final_mime.lower() or "audio" in final_mime.lower():
+         if "webm" in final_mime.lower():
-             try:
+             import imageio_ffmpeg
-                 # Usar tmp para cross-platform compatibility
+             ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
-                 with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
+             try:
-                     tmp_in.write(content)
+                 # Usar tmp para cross-platform compatibility
-                     tmp_in_name = tmp_in.name
+                 with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_in:
-                 tmp_out_name = tmp_in_name.replace(".webm", ".mp4")
+                     tmp_in.write(content)
- 
+                     tmp_in_name = tmp_in.name
-                 # Ejecutar FFMPEG (disponible via Aptfile en Railway)
+                 tmp_out_name = tmp_in_name.replace(".webm", ".mp4")
-                 # Utiliza codec aac compatible universal con .mp4
+ 
-                 result = subprocess.run([
+                 # Ejecutar FFMPEG (via imageio-ffmpeg PIP)
-                     'ffmpeg', '-y', '-i', tmp_in_name,
+                 result = subprocess.run([
-                     '-c:a', 'aac', '-b:a', '64k',
+                     ffmpeg_exe, '-y', '-i', tmp_in_name,
-                     tmp_out_name
+                     '-c:a', 'aac', '-b:a', '64k',
-                 ], capture_output=True)"""
+                     tmp_out_name
- 
+                 ], capture_output=True)"""
- new_code = """        # Conversion nativa WebM -> MP4 para WhatsApp Voice Notes
+ 
-         if "webm" in final_mime.lower():
+ text = re.sub(r'# Conversion nativa WebM.*?capture_output=True\)', new_block, text, flags=re.DOTALL)
-             import subprocess, os, tempfile
+ 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [text, new_block, text]
- **[convention] problem-fix in server.py — confirmed 3x**: -         if media_id:
+         if media_id and not media_id.startswith("ERROR_META:"):

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[what-changed] what-changed in requirements.txt**: - 
+ 
- 
+ imageio-ffmpeg
+ 
- **[what-changed] what-changed in requirements.txt**: - 
+ 
+ 
- **[convention] Added JWT tokens authentication — confirmed 3x**: - # ============================================================
+ # ============================================================
- #  whatsapp_client.py — Envía mensajes a WhatsApp via Meta API
+ #  whatsapp_client.py — Envía mensajes a WhatsApp via Meta API
- # ============================================================
+ # ============================================================
- import httpx
+ import httpx
- from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID, META_API_VERSION
+ from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID, META_API_VERSION
- 
+ 
- META_API_URL = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
+ META_API_URL = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
- 
+ 
- 
+ 
- def enviar_mensaje(numero_destino: str, texto: str, reply_to_wamid: str = None) -> bool:
+ def enviar_mensaje(numero_destino: str, texto: str, reply_to_wamid: str = None) -> bool:
-     """
+     """
-     Envía un mensaje de texto al número de WhatsApp indicado.
+     Envía un mensaje de texto al número de WhatsApp indicado.
- 
+ 
-     Args:
+     Args:
-         numero_destino: Número completo con código de país (ej: '51945257117')
+         numero_destino: Número completo con código de país (ej: '51945257117')
-         texto:          Texto del mensaje a enviar
+         texto:          Texto del mensaje a enviar
- 
+ 
-     Returns:
+     Returns:
-         wamid string si el envío fue exitoso, None si hubo error.
+         wamid string si el envío fue exitoso, None si hubo error.
-     """
+     """
-     headers = {
+     headers = {
-         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
+         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
-         "Content-Type": "application/json",
+         "Content-Type": "application/json",
-     }
+     }
- 
+ 
-     payload = {
+     payload = {
-         "messaging_product": "whatsapp",
+         "messag
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [META_API_URL, enviar_mensaje, enviar_media, enviar_mensaje_texto, obtener_media_url]
