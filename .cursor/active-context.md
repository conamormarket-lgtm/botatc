> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Reacci — protects against XSS and CSRF token theft**: -         elif tipo_mensaje == "location":
+         elif tipo_mensaje == "reaction":
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+             reaction_data = mensaje_data.get("reaction", {})
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+             emoji = reaction_data.get("emoji", "")
-             addr = mensaje_data.get("location", {}).get("address", "")
+             msg_id_reacted = reaction_data.get("message_id", "")
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+             
-         elif tipo_mensaje == "location":
+             texto_original = "un mensaje"
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+             if numero_wa in sesiones:
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+                 for m_hist in sesiones[numero_wa]["historial"]:
-             addr = mensaje_data.get("location", {}).get("address", "")
+                     if m_hist.get("msg_id") == msg_id_reacted:
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+                         txt = m_hist.get("content", "")
-         else:
+                         if txt.startswith("["): 
-             texto_cliente = f"[{tipo_mensaje}]"
+                             txt = txt.split("]")[0] + "]"
- 
+                         texto_original = (txt[:40] + '...') if len(txt) > 40 else txt
-     except (KeyError, IndexError):
+                         break
-         return {"status": "ok"}   # payload inesperado → ignorar sin error
+             
- 
+             if emoji:
-     # Detectar si el cliente está usando la función de deslizar/responder
+                 texto_cliente = f"[💬 Reacción: {emoji} a «{texto_original}»]"
-     contexto = changes["messages"][0].get("context", {})
+             else:
-     if "id" in contexto:
+                 texto_cliente = f"[❌ Quitó reacción a «{texto_original}»]"
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Fixed null crash in KeyError — protects against XSS and CSRF token theft**: -             texto_cliente = f"[📎 Archivo: {filename}]"
+             media_id = mensaje_data.get("document", {}).get("id", "")
-         elif tipo_mensaje == "location":
+             texto_cliente = f"[documento:{media_id}|{filename}]"
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+         elif tipo_mensaje == "location":
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+             lat = mensaje_data.get("location", {}).get("latitude", "")
-             addr = mensaje_data.get("location", {}).get("address", "")
+             lon = mensaje_data.get("location", {}).get("longitude", "")
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+             addr = mensaje_data.get("location", {}).get("address", "")
-         elif tipo_mensaje == "location":
+             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+         elif tipo_mensaje == "location":
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+             lat = mensaje_data.get("location", {}).get("latitude", "")
-             addr = mensaje_data.get("location", {}).get("address", "")
+             lon = mensaje_data.get("location", {}).get("longitude", "")
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+             addr = mensaje_data.get("location", {}).get("address", "")
-         else:
+             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
-             texto_cliente = f"[{tipo_mensaje}]"
+         else:
- 
+             texto_cliente = f"[{tipo_mensaje}]"
-     except (KeyError, IndexError):
+ 
-         return {"status": "ok"}   # payload inesperado → ignorar sin error
+     except (KeyError, IndexError):
- 
+         return {"status": "ok"}   # payload inesperado → ignorar sin error
-     # Detectar si el cliente está usando la función de deslizar/responder
+ 
-     conte
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Fixed null crash in Esperando — parallelizes async operations for speed**: -         burbujas += f"""
+ 
-         <div class="mensaje {lado}">
+         def wrap_phone(match):
-           <div class="remitente">{remitente}</div>
+             phone = match.group(1)
-           <div class="{clase}">{texto}</div>
+             clean_phone = __import__('re').sub(r'[\s\-]', '', phone)
-         </div>"""
+             if sum(c.isdigit() for c in clean_phone) >= 7:
- 
+                 return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
-     if not burbujas:
+             return phone
-         burbujas = '<p style="text-align:center;color:#aaa;padding:2rem">Sin mensajes aún en esta sesión</p>'
+         texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)
- 
+         burbujas += f"""
-     estado_badge = "🟢 Bot activo" if activo else "🔴 Esperando humano"
+         <div class="mensaje {lado}">
-     color_badge  = "#2e7d32" if activo else "#c62828"
+           <div class="remitente">{remitente}</div>
-     bg_badge     = "#e8f5e9" if activo else "#ffebee"
+           <div class="{clase}">{texto}</div>
- 
+         </div>"""
-     btn_reactivar = "" if activo else f"""
+ 
-     <form method="post" action="/admin/reactivar/{numero_wa}" style="margin:0">
+     if not burbujas:
-       <button style="background:#25d366;color:white;border:none;padding:.5rem 1rem;
+         burbujas = '<p style="text-align:center;color:#aaa;padding:2rem">Sin mensajes aún en esta sesión</p>'
-                      border-radius:8px;cursor:pointer;font-weight:600">▶ Reactivar bot</button>
+ 
-     </form>"""
+     estado_badge = "🟢 Bot activo" if activo else "🔴 Esperando humano"
- 
+     color_badge  = "#2e7d32" if activo else "#c62828"
-     return HTMLResponse(f"""
+     bg_badge     = "#e8f5e9" if acti
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Fixed null crash in Object — prevents null/undefined runtime crashes**: -             function renderQuickReplies(data) {
+             function renderQuickReplies(data) {{
-                 if(data.length === 0) {
+                 if(data.length === 0) {{
-                 }
+                 }}
-                 const groups = {};
+                 const groups = {{}};
-                 data.forEach(qr => {
+                 data.forEach(qr => {{
-                 });
+                 }});
-                 const isSearching = document.getElementById('qrSearchFilter') && document.getElementById('qrSearchFilter').value.trim() !== "";
+                 const searchInput = document.getElementById('qrSearchFilter');
-                 
+                 const isSearching = searchInput && searchInput.value.trim() !== "";
-                 Object.keys(groups).sort().forEach(cat => {
+                 
-                     const groupContainer = document.createElement("div");
+                 Object.keys(groups).sort().forEach(cat => {{
-                     groupContainer.style.cssText = "display:flex; flex-direction:column; gap:0.4rem; margin-bottom:0.2rem;";
+                     const groupContainer = document.createElement("div");
-                     
+                     groupContainer.style.cssText = "display:flex; flex-direction:column; gap:0.4rem; margin-bottom:0.2rem;";
-                     const catHeader = document.createElement("div");
+                     
-                     catHeader.style.cssText = "background:rgba(255,255,255,0.05); padding:0.6rem 0.8rem; border-radius:6px; cursor:pointer; display:flex; justify-content:space-between; align-items:center; font-weight:600; font-size:0.85rem; border:1px solid var(--accent-border); user-select:none; transition:background 0.2s;";
+                     const catHeader = document.createElement("div");
-                     catHeader.onmouseover = function() {this.style.background='rgba(255,255,255,0.08)';};
+                     catHeader.styl
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Fixed null crash in Agrupar — prevents null/undefined runtime crashes**: -             function renderQuickReplies(data) {{
+             function renderQuickReplies(data) {
-                 if(data.length === 0) {{
+                 if(data.length === 0) {
-                 }}
+                 }
-                 data.forEach(qr => {{
+                 
-                     const container = document.createElement("div");
+                 // Agrupar por categoría
-                     container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.65rem 0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
+                 const groups = {};
-                     container.onmouseover = function() {{this.style.borderColor='var(--primary-color)';}};
+                 data.forEach(qr => {
-                     container.onmouseout = function() {{this.style.borderColor='var(--accent-border)';}};
+                     const cat = qr.category && qr.category.trim() !== "" ? qr.category : "General";
-                     const btn = document.createElement("button");
+                     if(!groups[cat]) groups[cat] = [];
-                     btn.type = "button";
+                     groups[cat].push(qr);
-                     btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column; gap:0.25rem;";
+                 });
-                     // Title row
+                 
-                     const headerRow = document.createElement("div");
+                 // Variables de control de estado abierto (mantener abiertos los grupos al buscar)
-                     headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%;";
+                 const isSearching = document.getElementById('qrSearchFilter') && document.getElementById('qrSearchFilter').value.trim() !== "";
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]

### 📐 Generic Logic Conventions & Fixes
- **[convention] Fixed null crash in Opcional — wraps unsafe operation in error boundary — confirmed 3x**: -                         isRecording = true;
+                         mediaRecorder.canceled = false;
-                         
+                         isRecording = true;
-                         btnRecord.style.background = "#ef4444";
+                         if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'flex';
-                         btnRecord.style.color = "white";
+                         
-                         btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
+                         btnRecord.style.background = "#ef4444";
-                         
+                         btnRecord.style.color = "white";
-                         // Opcional: Mostrar que está grabando en el input
+                         btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
-                         const manualInput = document.getElementById("manualMsgInput");
+                         
-                         if(manualInput) {
+                         // Opcional: Mostrar que está grabando en el input
-                             manualInput.dataset.originalPlaceholder = manualInput.placeholder;
+                         const manualInput = document.getElementById("manualMsgInput");
-                             manualInput.placeholder = "🔴 Grabando audio... (Presiona el cuadro rojo para detener/enviar)";
+                         if(manualInput) {
-                         }
+                             manualInput.dataset.originalPlaceholder = manualInput.placeholder;
- 
+                             manualInput.placeholder = "🔴 Grabando audio... (Presiona el cuadro rojo para detener/enviar)";
-                     } cat
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] problem-fix in inbox.html**: - </body>
+ 
- 
+     <!-- Lightbox para imágenes -->
- </html>
+     <div id="imageLightbox" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; align-items:center; justify-content:center; flex-direction:column; cursor:pointer;" onclick="if(event.target === this) this.style.display='none'">
+         <button onclick="document.getElementById('imageLightbox').style.display='none'" style="position:absolute; top:20px; right:30px; background:none; border:none; color:white; font-size:2.5rem; cursor:pointer; text-shadow:0 2px 4px rgba(0,0,0,0.5);">&times;</button>
+         <img id="lightboxImg" src="" style="max-width:90%; max-height:90%; border-radius:8px; box-shadow:0 10px 40px rgba(0,0,0,0.7); cursor:default;" oncontextmenu="event.stopPropagation();">
+     </div>
+ 
+     <!-- Script de Lightbox -->
+     <script>
+         document.addEventListener('click', function(e) {
+             if (e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
+                 const alt = e.target.getAttribute('alt');
+                 if (alt && alt.startsWith('Imagen')) {
+                     const lb = document.getElementById('imageLightbox');
+                     const lbImg = document.getElementById('lightboxImg');
+                     if (lb && lbImg) {
+                         lbImg.src = e.target.src;
+                         lb.style.display = 'flex';
+                     }
+                 }
+             }
+         });
+     </script>
+ </body>
+ 
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
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
- **[what-changed] Updated stop database schema — adds runtime type validation before use**: - # Modify the record code
+ # 1. Update stop event listener to check `mediaRecorder.canceled`
- target = r"""            if (mediaRecorder && mediaRecorder.state === 'recording') {
+ target1 = r"""                        mediaRecorder.addEventListener("stop", async () => {
-                 mediaRecorder.stop();
+                             const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
-                 btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
+                             const formData = new FormData();"""
-                 btnRecord.style.color = "var(--text-main)";
+ replace1 = r"""                        mediaRecorder.addEventListener("stop", async () => {
-             } else {
+                             if (mediaRecorder.canceled) {
-                 try {
+                                 return; // Do not send audio if canceled
-                     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
+                             }
-                     mediaRecorder = new MediaRecorder(stream);
+                             const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
-                     audioChunks = [];
+                             const formData = new FormData();"""
-                     mediaRecorder.addEventListener("dataavailable", event => {
+ text = text.replace(target1, replace1)
-                         if(event.data.size > 0) audioChunks.push(event.data);
+ 
-                     });
+ # 2. Update mediaRecorder.start() logic
-                     mediaRecorder.addEventListener("stop", 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [text, target1, replace1, text, target2]
- **[convention] Fixed null crash in Archivo — protects against XSS and CSRF token theft — confirmed 8x**: -             media_id = mensaje_data.get("document", {}).get("id", "")
+             texto_cliente = f"[📎 Archivo: {filename}]"
-             texto_cliente = f"[documento:{media_id}|{filename}]" 
+         elif tipo_mensaje == "location":
-         elif tipo_mensaje == "location":
+             lat = mensaje_data.get("location", {}).get("latitude", "")
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+             lon = mensaje_data.get("location", {}).get("longitude", "")
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+             addr = mensaje_data.get("location", {}).get("address", "")
-             addr = mensaje_data.get("location", {}).get("address", "")
+             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+         elif tipo_mensaje == "location":
-         elif tipo_mensaje == "location":
+             lat = mensaje_data.get("location", {}).get("latitude", "")
-             lat = mensaje_data.get("location", {}).get("latitude", "")
+             lon = mensaje_data.get("location", {}).get("longitude", "")
-             lon = mensaje_data.get("location", {}).get("longitude", "")
+             addr = mensaje_data.get("location", {}).get("address", "")
-             addr = mensaje_data.get("location", {}).get("address", "")
+             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
-             texto_cliente = f"[ubicacion:{lat},{lon},{addr}]"
+         else:
-         else:
+             texto_cliente = f"[{tipo_mensaje}]"
-             texto_cliente = f"[{tipo_mensaje}]"
+ 
- 
+     except (KeyError, IndexError):
-     except (KeyError, IndexError):
+         return {"status": "ok"}   # payload inesperado → ignorar sin error
-         return {"status": "ok"}   # payload inesperado → ignorar sin error
+ 
- 
+     # Detectar si el cliente está usando la función de deslizar/responder
-     # De
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in Solo — parallelizes async operations for speed — confirmed 4x**: -         burbujas += f"""
+             
-         <div class="mensaje {lado}">
+             def wrap_phone(match):
-           <div class="remitente">{remitente}</div>
+                 phone = match.group(1)
-           <div class="{clase}">{texto}</div>
+                 clean_phone = re.sub(r'[\s\-]', '', phone)
-         </div>"""
+                 # Solo si tiene más de 6 dígitos
- 
+                 if sum(c.isdigit() for c in clean_phone) >= 7:
-     if not burbujas:
+                     # Escape seguro
-         burbujas = '<p style="text-align:center;color:#aaa;padding:2rem">Sin mensajes aún en esta sesión</p>'
+                     return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
- 
+                 return phone
-     estado_badge = "🟢 Bot activo" if activo else "🔴 Esperando humano"
+             texto = re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)
-     color_badge  = "#2e7d32" if activo else "#c62828"
+         burbujas += f"""
-     bg_badge     = "#e8f5e9" if activo else "#ffebee"
+         <div class="mensaje {lado}">
- 
+           <div class="remitente">{remitente}</div>
-     btn_reactivar = "" if activo else f"""
+           <div class="{clase}">{texto}</div>
-     <form method="post" action="/admin/reactivar/{numero_wa}" style="margin:0">
+         </div>"""
-       <button style="background:#25d366;color:white;border:none;padding:.5rem 1rem;
+ 
-                      border-radius:8px;cursor:pointer;font-weight:600">▶ Reactivar bot</button>
+     if not burbujas:
-     </form>"""
+         burbujas = '<p style="text-align:center;color:#aaa;padding:2rem">Sin mensajes aún en esta sesión</p>'
-     return HTMLResponse(f"""
+     estado_badge = "🟢 Bot activo" if activo else "🔴 Esperando humano"

… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[problem-fix] problem-fix in server.py**: -                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
+                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
