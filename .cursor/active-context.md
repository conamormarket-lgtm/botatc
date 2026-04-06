> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `serviceAccountKey.json` (Domain: **Config/Infrastructure**)

### 🔴 Config/Infrastructure Gotchas
- **⚠️ GOTCHA: Fixed null crash in ReaccionPayload**: - @app.post("/admin/toggle")
+ class ReaccionPayload(BaseModel):
- async def toggle_bot_global(request: Request):
+     wa_id: str
-     """Activa o desactiva el bot globalmente."""
+     message_id: str
-     global BOT_GLOBAL_ACTIVO
+     emoji: str
-     if not verificar_sesion(request):
+ 
-         raise HTTPException(status_code=403, detail="No autorizado")
+ @app.post("/api/admin/reaccionar")
-     BOT_GLOBAL_ACTIVO = not BOT_GLOBAL_ACTIVO
+ async def admin_reaccionar(payload: ReaccionPayload, request: Request):
-     estado = "ACTIVADO" if BOT_GLOBAL_ACTIVO else "APAGADO"
+     """Permite al operador reaccionar a un mensaje del usuario."""
-     print(f"  [\u26a1 Bot {estado} globalmente desde panel admin]")
+     if not verificar_sesion(request):
-     return RedirectResponse(url=f"/admin", status_code=303)
+         return {"ok": False, "error": "No autorizado"}
- 
+     
- @app.get("/api/debug/historial/{wa_id}")
+     from whatsapp_client import enviar_reaccion_async
- async def debug_historial(wa_id: str):
+     exito = await enviar_reaccion_async(payload.wa_id, payload.message_id, payload.emoji)
-     if wa_id in sesiones:
+     
-         return JSONResponse(sesiones[wa_id]["historial"])
+     if exito:
-     return {"status": "none"}
+         # Añadir al historial local? (Opcional, pero para mantener registro)
- 
+         s = sesiones.get(payload.wa_id)
- 
+         if s:
- 
+             s["historial"].append({"role": "assistant", "content": f"*[Reacción enviada: {payload.emoji}]*"})
- from fastapi.responses import Response
+             s["ultima_actividad"] = datetime.utcnow()
- 
+             try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(payload.wa_id, s)
- @app.get("/api/media/{media_id}")
+             except: pass
- async def get_media_proxy(request: Request, media_id: str):
+         return {"ok": True}
-     """Proxy para obtener imágenes o stickers de WhatsApp sin e
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]
- **⚠️ GOTCHA: Fixed null crash in Stickers**: -             </div>
+                 <button type="button" onclick="toggleStickersMenu()" style="padding: 0.35rem 0.8rem; border-radius: 20px; border: 1px solid var(--accent-border); background: var(--bg-main); cursor: pointer; font-size: 0.85rem; white-space: nowrap; color: var(--text-main); font-weight: 500; transition: background 0.2s;">😎 Stickers Extras</button>
-             <div id="replyPreviewContainer" style="display:none; align-items:center; justify-content:space-between; background:var(--accent-bg); padding: 0.5rem 1rem; border-left: 3px solid var(--primary-color); font-size: 0.85rem; color: var(--text-muted); border-radius: 8px 8px 0 0; margin-bottom: -0.5rem; position: relative;">
+             </div>
-                 <span style="font-family:var(--font-main);">Respondiendo a: <span id="replyPreviewTxt" style="color:var(--text-main);font-weight:600;">...</span></span>
+             <div id="replyPreviewContainer" style="display:none; align-items:center; justify-content:space-between; background:var(--accent-bg); padding: 0.5rem 1rem; border-left: 3px solid var(--primary-color); font-size: 0.85rem; color: var(--text-muted); border-radius: 8px 8px 0 0; margin-bottom: -0.5rem; position: relative;">
-                 <button type="button" onclick="document.getElementById('replyPreviewContainer').style.display='none'; document.getElementById('replyToWamid').value='';" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:1.1rem;padding:0;">×</button>
+                 <span style="font-family:var(--font-main);">Respondiendo a: <span id="replyPreviewTxt" style="color:var(--text-main);font-weight:600;">...</span></span>
-             </div>
+                 <button type="button" onclick="document.getElementById('replyPreviewContainer').style.display='none'; document.getElementById('replyToWamid').value='';" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:1.1rem;padding:0;">×</butto
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]

### 📐 Config/Infrastructure Conventions & Fixes
- **[what-changed] what-changed in inbox.html**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Inter — prevents null/undefined runtime crashes**: -     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&display=swap" rel="stylesheet">
+     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
-     <style>
+     <script type="module" src="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js"></script>
-         :root {
+     <style>
-             /* 1. Nivel de Color Principal */
+         :root {
-             --primary-color: #3b82f6;       
+             /* 1. Nivel de Color Principal */
-             --primary-hover: #2563eb;       
+             --primary-color: #3b82f6;       
-             /* 2. Nivel de Color de Acento */
+             --primary-hover: #2563eb;       
-             --accent-bg: #1e293b;           
+             /* 2. Nivel de Color de Acento */
-             --accent-border: #334155;       
+             --accent-bg: #1e293b;           
-             --accent-hover-soft: #334155;   
+             --accent-border: #334155;       
-             /* 3. Nivel de Color de Fondo General */
+             --accent-hover-soft: #334155;   
-             --bg-main: #0f172a;             
+             /* 3. Nivel de Color de Fondo General */
-             /* 4. Tipografías */
+             --bg-main: #0f172a;             
-             --font-main: 'Inter', sans-serif;
+             /* 4. Tipografías */
-             --font-heading: 'Outfit', sans-serif;
+             --font-main: 'Inter', sans-serif;
-             /* Otros */
+             --font-heading: 'Outfit', sans-serif;
-             --text-main: #f8fafc;           
+             /* Otros */
-             --text-muted: #94a3b8;          
+             --text-main: #f8fafc;           
-             --danger-color: #ef4444;        
+             --text-muted: #94a3b8;          
-             --success-color: #10b981;       
+             --danger-c
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in True**: -     
+     escalados   = [(n, s) for n, s in sesiones.items() if not s["bot_activo"] and s.get("escalado_en")]
-     # SECCIÓN NUEVA: BUSCADOR / NUEVO CHAT en el HTML de admin (o inbox)
+     escalados.sort(key=lambda x: x[1]["escalado_en"], reverse=True)
-     # Nota: La instrucción pide insertar esto en el div list-header de inbox.html
+     n_escalados = len(escalados)
-     # Aquí se mantiene la lógica de sesiones existente.
+     n_activos   = sum(1 for s in sesiones.values() if s["bot_activo"])
-     
+ 
-     escalados   = [(n, s) for n, s in sesiones.items() if not s["bot_activo"] and s.get("escalado_en")]
+     def tiempo_relativo(dt):
-     escalados.sort(key=lambda x: x[1]["escalado_en"], reverse=True)
+         diff = ahora - dt
-     n_escalados = len(escalados)
+         m = int(diff.total_seconds() / 60)
-     n_activos   = sum(1 for s in sesiones.values() if s["bot_activo"])
+         if m < 1:   return "ahora"
- 
+         if m < 60:  return f"hace {m}m"
-     def tiempo_relativo(dt):
+         return f"hace {m//60}h {m%60}m"
-         diff = ahora - dt
+ 
-         m = int(diff.total_seconds() / 60)
+     def ultimo_msg(sesion):
-         if m < 1:   return "ahora"
+         hist = [m for m in sesion.get("historial", []) if m["role"] != "system"]
-         if m < 60:  return f"hace {m}m"
+         if not hist: return "—"
-         return f"hace {m//60}h {m%60}m"
+         return hist[-1]["content"][:60] + ("…" if len(hist[-1]["content"]) > 60 else "")
-     def ultimo_msg(sesion):
+     # ── Tabla: Esperando humano ──────────────────────────
-         hist = [m for m in sesion.get("historial", []) if m["role"] != "system"]
+     filas_esc = ""
-         if not hist: return "—"
+     for num, s in escalados:
-         return hist[-1]["content"][:60] + ("…" if len(hist[-1]["content"]) > 60 else "")
+         hace   = tiempo_relativo(s["escalado_en"])
- 
+         nombre = s.get("nombre_cliente", num)
-     
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]
- **[decision] Optimized PERSISTENCIA**: + # ============================================================
+ #  PERSISTENCIA DE STICKERS EN FIRESTORE
+ # ============================================================
+ import base64
+ 
+ def guardar_sticker_en_bd(filename: str, file_bytes: bytes):
+     """Guarda físicamente un archivo en la base de datos convirtiéndolo a Base64."""
+     db = inicializar_firebase()
+     b64_data = base64.b64encode(file_bytes).decode('utf-8')
+     db.collection("bot_stickers").document(filename).set({
+         "filename": filename,
+         "base64": b64_data,
+         "updatedAt": firestore.SERVER_TIMESTAMP
+     })
+ 
+ def cargar_stickers_de_bd(directorio: str):
+     """Descarga todos los stickers desde Firestore al directorio temporal en memoria."""
+     db = inicializar_firebase()
+     docs = db.collection("bot_stickers").limit(300).stream()
+     import os
+     os.makedirs(directorio, exist_ok=True)
+     count = 0
+     for doc in docs:
+         try:
+             data = doc.to_dict()
+             filename = data.get("filename")
+             b64 = data.get("base64")
+             if filename and b64:
+                 filepath = os.path.join(directorio, filename)
+                 with open(filepath, "wb") as f:
+                     f.write(base64.b64decode(b64))
+                 count += 1
+         except Exception as e:
+             print(f"Error cargando sticker {doc.id}: {e}")
+     return count
+ 

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id, guardar_sesion_chat]
- **[convention] Fixed null crash in GICA — confirmed 4x**: -         };
+         // LÓGICA DE SUBIDA DE IMÁGENES/STICKERS DIRECTAS (Pegar o click)
- 
+         const uploadMedia = async (file) => {
-         // LÓGICA DE SUBIDA DE IMÁGENES/STICKERS DIRECTAS (Pegar o click)
+             const input = document.getElementById('manualMsgInput');
-         const uploadMedia = async (file) => {
+             if(!input) return;
-             const input = document.getElementById('manualMsgInput');
+             
-             if(!input) return;
+             // UI Feedback
-             
+             input.placeholder = "Subiendo imagen a WhatsApp... ⏳";
-             // UI Feedback
+             input.disabled = true;
-             input.placeholder = "Subiendo imagen a WhatsApp... ⏳";
+             
-             input.disabled = true;
+             const formData = new FormData();
-             
+             formData.append("file", file);
-             const formData = new FormData();
+             
-             formData.append("file", file);
+             try {
-             
+                 const res = await fetch('/api/admin/upload_media', {
-             try {
+                     method: 'POST',
-                 const res = await fetch('/api/admin/upload_media', {
+                     body: formData
-                     method: 'POST',
+                 });
-                     body: formData
+                 const data = await res.json();
-                 });
+                 
-                 const data = await res.json();
+                 if(data.ok && data.media_id) {
-                 
+                     input.value += `[imagen:${data.media_id}] `;
-                 if(data.ok && data.media_id) {
+                 } else {
-                     input.value += `[imagen:${data.media_id}] `;
+                     alert("Error subiendo: " + (data.error || "Desconocido"));
-                 } else {
+                 }
-                     alert("Error su
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in server.py**: -             burbujas += f'<div class="bubble {clase} {lado}" onclick="document.getElementById(\\'manualMsgInput\\').value = \\'> \\' + this.innerText.trim() + \\'\\\\n\\\\n\\' + document.getElementById(\\'manualMsgInput\\').value; document.getElementById(\\'manualMsgInput\\').focus();" style="cursor:pointer;" title="Click para citar este mensaje">{texto_renderizado}</div>'
+             burbujas += f"""<div class="bubble {clase} {lado}" onclick="document.getElementById('manualMsgInput').value = '> ' + this.innerText.trim() + '\\n\\n' + document.getElementById('manualMsgInput').value; document.getElementById('manualMsgInput').focus();" style="cursor:pointer;" title="Click para citar este mensaje">{texto_renderizado}</div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]
- **[problem-fix] problem-fix in server.py**: -                     return f'<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display:inline-block;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/150x150?text=Sticker\';"></div>'
+                     return f"""<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display:inline-block;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/150x150?text=Sticker';"></div>"""
-                     return f'<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/250x150?text=Imagen\';"></div>'
+                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]
- **[what-changed] what-changed in prompts.py**: -     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenda.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de mujer)
+     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenda.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de mujer y es su primer mensaje)
-     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenido.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de hombre)
+     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenido.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de hombre y es su primer mensaje)

📌 IDE AST Context: Modified symbols likely include [_GUIA_CACHE, _obtener_guia, get_system_prompt, MENSAJE_BIENVENIDA]
- **[what-changed] what-changed in config.py**: - GEMINI_MODEL   = "gemini-1.5-flash"
+ GEMINI_MODEL   = "gemini-2.5-flash"

📌 IDE AST Context: Modified symbols likely include [DOCUMENTOS_GUIA, LM_STUDIO_BASE_URL, LM_STUDIO_API_KEY, LM_STUDIO_MODEL, GEMINI_API_KEY]
- **[convention] Fixed null crash in RedirectResponse — confirmed 3x**: - 
+         try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesiones[numero_wa])
-     form_data = await request.form()
+         except: pass
-     redirect_url = form_data.get("redirect", "/admin")
+ 
-     return RedirectResponse(url=redirect_url, status_code=303)
+     form_data = await request.form()
- 
+     redirect_url = form_data.get("redirect", "/admin")
- @app.post("/api/admin/pausar/{numero_wa}")
+     return RedirectResponse(url=redirect_url, status_code=303)
- async def pausar_bot_manual(request: Request, numero_wa: str):
+ 
-     """Pausa al bot de forma manual para un WA específico."""
+ @app.post("/api/admin/pausar/{numero_wa}")
-     if not verificar_sesion(request):
+ async def pausar_bot_manual(request: Request, numero_wa: str):
-         return RedirectResponse(url="/login", status_code=303)
+     """Pausa al bot de forma manual para un WA específico."""
- 
+     if not verificar_sesion(request):
-     if numero_wa in sesiones:
+         return RedirectResponse(url="/login", status_code=303)
-         sesiones[numero_wa]["bot_activo"] = False
+ 
-         sesiones[numero_wa]["escalado_en"] = datetime.utcnow()
+     if numero_wa in sesiones:
-         sesiones[numero_wa]["motivo_escalacion"] = "Intervención manual forzada"
+         sesiones[numero_wa]["bot_activo"] = False
-         print(f"  [⏸ Bot pausado manualmente para {numero_wa}]")
+         sesiones[numero_wa]["escalado_en"] = datetime.utcnow()
-         
+         sesiones[numero_wa]["motivo_escalacion"] = "Intervención manual forzada"
-     form_data = await request.form()
+         print(f"  [⏸ Bot pausado manualmente para {numero_wa}]")
-     redirect_url = form_data.get("redirect", f"/inbox/{numero_wa}")
+         try: from firebase_client import guardar_sesion_chat; guardar_sesion_chat(numero_wa, sesiones[numero_wa])
-     return RedirectResponse(url=redirect_url, status_code=303)
+         except: pass
-
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, BOT_GLOBAL_ACTIVO]
- **[discovery] discovery in prompts.py**: - 10. USO DE STICKERS: Tienes la capacidad de usar stickers. Cuando sea útil ser dinámica 
+ 10. USO DE STICKERS: Tienes un pequeño catálogo de stickers oficiales para ser más dinámica. 
-     (ej: agradecer, celebrar que llegó, lamentar retraso), agrega una etiqueta al final de tu respuesta: 
+     ESTÁ ESTRICTAMENTE PROHIBIDO inventar URLs o usar imágenes que no estén en esta lista.
-     [sticker:https://dummyimage.com/150x150/000/fff.png&text=Sticker] o busca URLs válidas y graciosas (puedes inventar o usar links gif directos terminados en png/jpg o Giphy si crees que funcionan).
+     Para usarlos, copia y pega EXACTAMENTE la etiqueta a continuación al final de tu respuesta:
- 
+     - [sticker:https://raw.githubusercontent.com/conamormarket lgtm/botatc/refs/heads/main/stickers/bendiciones.webp]  -> (Usa este para cuando el cliente se despide)
- ESCALACIÓN A HUMANO — MUY IMPORTANTE:
+     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenda.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de mujer)
- Cuando detectes CUALQUIERA de estas situaciones, agrega [ESCALAR] al FINAL de tu respuesta:
+     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/bienvenido.webp]  -> (Usa este para darle la bienvenida al cliente si tiene nombre de hombre)
- - El cliente pide explícitamente hablar con una persona, asesor, encargado o humano.
+     - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/buenas%20tardes.webp]  -> (Usa este si el primer mensaje del cliente llega entre las 12pm y las 5:59pm y el cliente dijo buenas tardes)
- - El cliente expresa frustración intensa, molestia fuerte o amenaza con queja formal.
+     - [sticker:http://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/claro%20que%20si.webp]  -> (Usa este si tu respuesta es positiva para algo que el cliente te pida que
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [_GUIA_CACHE, _obtener_guia, get_system_prompt, MENSAJE_BIENVENIDA]
- **[what-changed] Updated configuration OpenAI — externalizes configuration for environment fle...**: - from openai import OpenAI
+ from dotenv import load_dotenv
- client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'), base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
+ load_dotenv()
- try:
+ from openai import OpenAI
-     resp = client.chat.completions.create(model='gemini-2.0-flash', messages=[{'role': 'user', 'content': 'hola'}])
+ client = OpenAI(api_key=os.getenv('GEMINI_API_KEY'), base_url='https://generativelanguage.googleapis.com/v1beta/openai/')
-     print('OK', resp)
+ try:
- except Exception as e:
+     resp = client.chat.completions.create(model='gemini-2.0-flash', messages=[{'role': 'user', 'content': 'hola'}])
-     import traceback
+     print('OK', resp)
-     traceback.print_exc()
+ except Exception as e:
- 
+     import traceback
+     traceback.print_exc()
+ 

📌 IDE AST Context: Modified symbols likely include [client, resp]
- **[discovery] discovery in pedidos_observer.py**: - from bot_atc import limpiar_telefono
+ 

📌 IDE AST Context: Modified symbols likely include [ORDEN_ETAPAS, cache_pedidos, notificar_whatsapp, _enviar_plantilla_1, _enviar_plantilla_2]
