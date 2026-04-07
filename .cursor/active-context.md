> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `check_js2.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in HTMLResponse**: -     html = html.replace("{chat_viewer_html}", chat_viewer_html)
+     html = html.replace("{labels_filter_html}", labels_filter_html)
-     html = html.replace("{chat_view_css}", chat_view_css)
+     html = html.replace("{chat_viewer_html}", chat_viewer_html)
-     html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
+     html = html.replace("{chat_view_css}", chat_view_css)
-     
+     html = html.replace("{color_global}", "#10b981" if BOT_GLOBAL_ACTIVO else "#ef4444")
-     return HTMLResponse(html)
+     
- 
+     return HTMLResponse(html)
- @app.get("/inbox", response_class=HTMLResponse)
+ 
- async def inbox_main(request: Request, tab: str = "all"):
+ @app.get("/inbox", response_class=HTMLResponse)
-     return renderizar_inbox(request, None, tab)
+ async def inbox_main(request: Request, tab: str = "all", label: str = None):
- 
+     return renderizar_inbox(request, None, tab, label)
- from typing import List
+ 
- 
+ from typing import List
- @app.post("/api/admin/stickers/upload")
+ 
- async def upload_stickers(files: List[UploadFile] = File(...)):
+ @app.post("/api/admin/stickers/upload")
-     """Recibe múltiples archivos webp/png, los guarda en disco ephemeral y sincroniza a Firestore."""
+ async def upload_stickers(files: List[UploadFile] = File(...)):
-     try:
+     """Recibe múltiples archivos webp/png, los guarda en disco ephemeral y sincroniza a Firestore."""
-         import os
+     try:
-         from firebase_client import guardar_sticker_en_bd
+         import os
-         os.makedirs("static/stickers", exist_ok=True)
+         from firebase_client import guardar_sticker_en_bd
-         count = 0
+         os.makedirs("static/stickers", exist_ok=True)
-         for file in files:
+         count = 0
-             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
+         for file in files:
-                 # Extraemos solo el nombre del archivo, 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Fixed null crash in None**: -         chat_viewer_html = f"""
+         session_tags = s.get("etiquetas", [])
-         {status_bar}
+         tags_bar = ""
-         <div style="padding:1.5rem;border-bottom:1px solid var(--accent-border);display:flex;align-items:center;background:var(--bg-main);">
+         for tid in session_tags:
-             <a href="/inbox?tab={tab}" class="btn-responsive-back" title="Volver a la lista">
+             lbl = next((l for l in global_labels if l.get("id") == tid), None)
-                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
+             if lbl:
-             </a>
+                 tags_bar += f'<span style="background:{lbl["color"]}22; color:{lbl["color"]}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {lbl["color"]}44;">{lbl["name"]}</span>'
-             <div style="width:40px;height:40px;border-radius:50%;background:var(--primary-color);color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;margin-right:1rem;font-size:1.2rem;flex-shrink:0">{nombre_chat[0].upper()}</div>
+ 
-             <div style="min-width:0">
+         chat_viewer_html = f"""
-                 <h3 style="margin:0;font-size:1.1rem;font-family:var(--font-heading);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{nombre_chat}</h3>
+         {status_bar}
-                 <small style="color:var(--text-muted)">+{wa_id}</small>
+         <div style="padding:1.5rem;border-bottom:1px solid var(--accent-border);display:flex;align-items:center;background:var(--bg-main);">
-             </div>
+             <a href="/inbox?tab={tab}" class="btn-responsive-back" title="Volver a la lista">
-         </div>
+                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: Updated typing database schema**: - 
+ 
+ 
+ # ============================================================
+ #  API DE GESTOR DE ETIQUETAS Y ASIGNACIONES
+ # ============================================================
+ 
+ from typing import Optional
+ 
+ class LabelPayload(BaseModel):
+     id: str
+     name: Optional[str] = None
+     color: Optional[str] = None
+ 
+ @app.post("/api/admin/labels/save")
+ async def api_save_label(payload: LabelPayload, request: Request):
+     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
+     from firebase_client import guardar_etiqueta_bd
+     guardar_etiqueta_bd(payload.id, payload.name, payload.color)
+     global global_labels
+     global_labels = [l for l in global_labels if l.get("id") != payload.id]
+     global_labels.append({"id": payload.id, "name": payload.name, "color": payload.color})
+     return {"ok": True}
+ 
+ @app.post("/api/admin/labels/delete")
+ async def api_delete_label(payload: LabelPayload, request: Request):
+     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
+     from firebase_client import eliminar_etiqueta_bd
+     eliminar_etiqueta_bd(payload.id)
+     global global_labels
+     global_labels = [l for l in global_labels if l.get("id") != payload.id]
+     
+     # Quitar etiqueta de sesiones cargadas
+     for k, s in sesiones.items():
+         if "etiquetas" in s and payload.id in s["etiquetas"]:
+             s["etiquetas"].remove(payload.id)
+     return {"ok": True}
+ 
+ @app.get("/api/admin/labels/list")
+ async def api_list_labels(request: Request):
+     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
+     return {"ok": True, "labels": global_labels}
+ 
+ class AssignLabelPayload(BaseModel):
+     wa_id: str
+     label_ids: list
+ 
+ @app.post("/api/admin/chats/labels")
+ async def api_assign_cha
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] what-changed in .gitignore**: - 隧道_log.txt
+ 隧道_log.txt
- **[problem-fix] Fixed null crash in HTMLResponse — prevents null/undefined runtime crashes**: -     if not verificar_sesion(request):
+     # Si las etiquetas están vacías por un hot-reload fallido, recuperarlas
-         return HTMLResponse(obtener_login_html(), status_code=401)
+     global global_labels
- 
+     if not global_labels:
-     import os
+         try:
-     if not os.path.exists("inbox.html"): return HTMLResponse("404: inbox.html no encontrado")
+             from firebase_client import cargar_etiquetas_bd
-         
+             global_labels = cargar_etiquetas_bd()
-     with open("inbox.html", "r", encoding="utf-8") as f:
+         except: pass
-         html = f.read()
+ 
- 
+     if not verificar_sesion(request):
-     ahora = datetime.utcnow()
+         return HTMLResponse(obtener_login_html(), status_code=401)
-     
+ 
-     def tiempo_relativo(dt):
+     import os
-         diff = ahora - dt
+     if not os.path.exists("inbox.html"): return HTMLResponse("404: inbox.html no encontrado")
-         m = int(diff.total_seconds() / 60)
+         
-         if m < 1:   return "ahora"
+     with open("inbox.html", "r", encoding="utf-8") as f:
-         if m < 60:  return f"{m}m"
+         html = f.read()
-         if m < 1440: return f"{m//60}h"
+ 
-         return f"{m//1440}d"
+     ahora = datetime.utcnow()
- 
+     
-     def ultimo_msg(sesion):
+     def tiempo_relativo(dt):
-         hist = [m for m in sesion.get("historial", []) if m["role"] != "system"]
+         diff = ahora - dt
-         if not hist: return "—"
+         m = int(diff.total_seconds() / 60)
-         return hist[-1]["content"][:50] + ("…" if len(hist[-1]["content"]) > 50 else "")
+         if m < 1:   return "ahora"
- 
+         if m < 60:  return f"{m}m"
-     # Procesar Lista de Chats
+         if m < 1440: return f"{m//60}h"
-     todas = sorted(sesiones.items(), key=lambda x: x[1]["ultima_actividad"], reverse=True)
+         return f"{m//1440}d"
-     lista_chats_html = ""
+ 
-     
+     def ultimo_msg(ses
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in Simular — confirmed 3x**: -                     document.getElementById('rightSidebar').style.display = 'none';
+                     
-                     if (window.enviarMensajeManual) {{
+                     document.getElementById('rightSidebar').style.display = 'none';
-                         window.enviarMensajeManual(new Event('submit'), '{wa_id}');
+                     
-                     }}
+                     // Simular clic en el botón de "Enviar" del formulario
-                 }}
+                     const form = input.closest('form');
-             }}
+                     if(form) {{
-             function checkQuickReplyTrigger(input) {{
+                         const btn = form.querySelector('button[type="submit"]');
-                 if(input.value.endsWith("/")) {{
+                         if(btn) btn.click();
-                     const side = document.getElementById('rightSidebar');
+                     }}
-                     if(side){{
+                 }}
-                         side.style.display = 'flex';
+             }}
-                         cargarQuickReplies();
+             function checkQuickReplyTrigger(input) {{
-                         setTimeout(()=> document.getElementById('qrSearchFilter').focus(), 50);
+                 if(input.value.endsWith("/")) {{
-                     }}
+                     const side = document.getElementById('rightSidebar');
-                 }}
+                     if(side){{
-             }}
+                         side.style.display = 'flex';
-             
+                         cargarQuickReplies();
-             function abrirModalCrearQR() {{
+                         setTimeout(()=> document.getElementById('qrSearchFilter').focus(), 50);
-                 const m = document.getElementById('qrCreateModal');
+                     }}
-                 if(m) {{
+                 }}
-                     document.getElementById('newQrTitle').value = '';

… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[problem-fix] Added error handling Respuestas — wraps unsafe operation in error boundary**: -             async function cargarQuickReplies() {
+             async function cargarQuickReplies() {{
-                 try {
+                 try {{
-                 } catch(e) {
+                 }} catch(e) {{
-                 }
+                 }}
-             }
+             }}
-             function renderQuickReplies(data) {
+             function renderQuickReplies(data) {{
-                 if(data.length === 0) {
+                 if(data.length === 0) {{
-                 }
+                 }}
-                 data.forEach(qr => {
+                 data.forEach(qr => {{
-                     btn.onmouseover = function() {this.style.background='var(--accent-hover-soft)';};
+                     btn.onmouseover = function() {{this.style.background='var(--accent-hover-soft)';}};
-                     btn.onmouseout = function() {this.style.background='none';};
+                     btn.onmouseout = function() {{this.style.background='none';}};
-                 });
+                 }});
-             }
+             }}
-             function filtrarQuickReplies(val) {
+             function filtrarQuickReplies(val) {{
-             }
+             }}
-             function aplicarQuickReply(text) {
+             function aplicarQuickReply(text) {{
-                 if(input) {
+                 if(input) {{
-                     const slashMatch = textBefore.match(/(?:^|\s)\/$/); 
+                     const slashMatch = textBefore.match(/(?:^|\\s)\/$/); 
-                     if (slashMatch) {
+                     if (slashMatch) {{
-                     } else {
+                     }} else {{
-                     }
+                     }}
-                 }
+                 }}
-             }
+             }}
-             function checkQuickReplyTrigger(input) {
+             function checkQuickReplyTrigger(input) {{
-                 if(input.value.endsWith("/")) {
+                 if(in
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[what-changed] 🟢 Edited serviceAccountKey.json (19 changes, 474min)**: Active editing session on serviceAccountKey.json.
19 content changes over 474 minutes.
- **[convention] Fixed null crash in PLANTILLAS — confirmed 5x**: - 
+         });
-             const filterMenu = document.getElementById('inboxFilterMenu');
+ 
-             if(filterMenu && !e.target.closest('#inboxFilterMenu') && !e.target.closest('button') && !e.target.closest('svg')) {
+         // ================= PLANTILLAS LOGIC =================
-                 filterMenu.style.display = 'none';
+         async function cargarPlantillas() {
-             }
+             const list = document.getElementById("templateList");
-         });
+             if(!list) return;
- 
+             list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Cargando...</div>`;
-         // ================= PLANTILLAS LOGIC =================
+             try {
-         async function cargarPlantillas() {
+                 const res = await fetch("/api/admin/templates/list");
-             const list = document.getElementById("templateList");
+                 const data = await res.json();
-             if(!list) return;
+                 if(data.ok) {
-             list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Cargando...</div>`;
+                     list.innerHTML = "";
-             try {
+                     if(data.plantillas.length === 0) {
-                 const res = await fetch("/api/admin/templates/list");
+                         list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Sin plantillas. Apreta (+) para añadir.</div>`;
-                 const data = await res.json();
+                     } else {
-                 if(data.ok) {
+                         data.plantillas.forEach(p => {
-                     list.innerHTML = "";
+                             const btn = document.createElement("div");
-                     if(data.plantillas.length === 0) {
+                             btn.style.cssText = "
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in inbox.html**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html, cargarChatLabels]
- **[what-changed] what-changed in inbox.html**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 5x**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in server.py — confirmed 3x**: - async def inbox_chat(request: Request, wa_id: str, tab: str = "all"):
+ async def inbox_chat(request: Request, wa_id: str, tab: str = "all", label: str = None):
-     return renderizar_inbox(request, wa_id, tab)
+     return renderizar_inbox(request, wa_id, tab, label)

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in None — confirmed 3x**: -         tags_html = ""
+         if session_tags is None: session_tags = []
-         if session_tags:
+         tags_html = ""
-             tags_html = '<div style="display:flex; gap:0.3rem; margin-top:0.3rem; flex-wrap:wrap;">'
+         if session_tags:
-             for tid in session_tags:
+             tags_html = '<div style="display:flex; gap:0.3rem; margin-top:0.3rem; flex-wrap:wrap;">'
-                 lbl = next((l for l in global_labels if l.get("id") == tid), None)
+             for tid in session_tags:
-                 if lbl:
+                 lbl = next((l for l in global_labels if l.get("id") == tid), None)
-                     tags_html += f'<span style="background:{lbl["color"]}22; color:{lbl["color"]}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {lbl["color"]}44;">{lbl["name"]}</span>'
+                 if lbl:
-             tags_html += '</div>'
+                     col = lbl.get("color", "#94a3b8")
-             
+                     nm = lbl.get("name", "Etiqueta")
-         lista_chats_html += f"""
+                     tags_html += f'<span style="background:{col}22; color:{col}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {col}44;">{nm}</span>'
-         <a href="/inbox/{num}?tab={tab}" class="chat-row {active_class}">
+             tags_html += '</div>'
-             <div class="chat-row-header">
+             
-                 <span class="chat-name">{nombre}</span>
+         lista_chats_html += f"""
-                 <span class="chat-time">{time_str}</span>
+         <a href="/inbox/{num}?tab={tab}" class="chat-row {active_class}">
-             </div>
+             <div class="chat-row-header">
-             <div class="chat-preview">{preview}</div>
+                 <span class="chat-name">{nombre}</span>
-             <div class="chat-badges">{badge_html}</div>
+                 <span clas
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in Error — prevents null/undefined runtime crashes — confirmed 7x**: -                     }
+                     }
-                 }
+                 }
-             } catch (e) {
+             } catch (e) {
-                 console.warn('Error en Live Chat Polling:', e);
+                 console.warn('Error en Live Chat Polling:', e);
-             }
+             }
-         }, 1500);
+         }, 1500);
- 
+ 
-         // API CLIENT PARA RESPONDER
+         // API CLIENT PARA RESPONDER
-         window.enviarMensajeManual = async function(e, wa_id) {
+         window.enviarMensajeManual = async function(e, wa_id) {
-             e.preventDefault();
+             e.preventDefault();
-             const input = document.getElementById('manualMsgInput');
+             const input = document.getElementById('manualMsgInput');
-             if(!input) return;
+             if(!input) return;
-             const msj = input.value.trim();
+             const msj = input.value.trim();
-             if(!msj) return;
+             if(!msj) return;
-             
+             
-             // Vaciar y enfocar
+             // Vaciar y enfocar
-             input.value = '';
+             input.value = '';
-             input.focus();
+             input.focus();
-             
+             
-             // Dibujado optimista instantáneo
+             // Dibujado optimista instantáneo
-             const scroll = document.getElementById('chatScroll');
+             const scroll = document.getElementById('chatScroll');
-             if(scroll) {
+             if(scroll) {
-                 const bubble = document.createElement('div');
+                 const bubble = document.createElement('div');
-                 bubble.className = "bubble bubble-bot lado-izq";
+                 bubble.className = "bubble bubble-bot lado-izq";
-                 bubble.style.border = "1px solid var(--primary-color)";
+                 bubble.style.border = "1px solid var(--primary-color)";
-                 bubble.innerText 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
