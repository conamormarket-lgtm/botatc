> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `serviceAccountKey.json` (Domain: **Config/Infrastructure**)

### 🔴 Config/Infrastructure Gotchas
- **⚠️ GOTCHA: Fixed null crash in Response**: - # ─────────────────────────────────────────────
+ from fastapi.responses import Response
- #  Health check
+ 
- # ─────────────────────────────────────────────
+ @app.get("/api/media/{media_id}")
- 
+ async def get_media_proxy(request: Request, media_id: str):
- @app.get("/")
+     """Proxy para obtener imágenes o stickers de WhatsApp sin exponer el token cliente."""
- async def home_redirect():
+     if not verificar_sesion(request):
-     return RedirectResponse("/inbox", status_code=303)
+         raise HTTPException(status_code=403, detail="No autorizado")
- 
+         
- @app.get("/health")
+     from whatsapp_client import obtener_media_url, descargar_media
- async def health():
+     url = await obtener_media_url(media_id)
-     return {"status": "ok", "bot": "IA-ATC", "sesiones": len(sesiones)}
+     if not url:
- 
+         return Response(content=b"", status_code=404)
- 
+         
- @app.get("/admin/chat/{numero_wa}", response_class=HTMLResponse)
+     contenido, mime_type = await descargar_media(url)
- async def ver_chat(request: Request, numero_wa: str):
+     if not contenido:
-     """Vista de conversación estilo WhatsApp para un número específico."""
+         return Response(content=b"", status_code=404)
-     if not verificar_sesion(request):
+         
-         return RedirectResponse(url=f"/admin", status_code=302)
+     return Response(content=contenido, media_type=mime_type or "image/jpeg")
-     sesion = sesiones.get(numero_wa)
+ 
-     if not sesion:
+ # ─────────────────────────────────────────────
-         return HTMLResponse("<h2 style='font-family:sans-serif;padding:2rem'>Sesión no encontrada o ya expiró.</h2>")
+ #  Health check
- 
+ # ─────────────────────────────────────────────
-     nombre  = sesion.get("nombre_cliente", numero_wa)
+ 
-     pedido  = sesion.get("datos_pedido", {}).get("id", "—") if sesion.get("datos_pedido") else "—"
+ @app.get("/")
-     estado  = sesion.get("datos
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **⚠️ GOTCHA: Fixed null crash in Reactivar**: -         # Reset completo de la sesión para ese número
+         # Reactivar el bot sin borrar el historial ni los datos del pedido vinculados
-         sesiones[numero_wa] = {
+         sesiones[numero_wa]["bot_activo"] = True
-             "historial":         [{"role": "system", "content": get_system_prompt()}],
+         sesiones[numero_wa]["escalado_en"] = None
-             "datos_pedido":      None,
+         sesiones[numero_wa]["motivo_escalacion"] = None
-             "bot_activo":        True,
+         sesiones[numero_wa]["ultima_actividad"] = datetime.utcnow()
-             "ultima_actividad":  datetime.utcnow(),
+         print(f"  [▶ Bot reactivado para {numero_wa} desde panel admin]")
-             "escalado_en":       None,
+ 
-             "motivo_escalacion": None,
+     form_data = await request.form()
-             "nombre_cliente":    sesiones[numero_wa].get("nombre_cliente", "Cliente"),
+     redirect_url = form_data.get("redirect", "/admin")
-         }
+     return RedirectResponse(url=redirect_url, status_code=303)
-         print(f"  [▶ Bot reactivado para {numero_wa} desde panel admin]")
+ 
- 
+ @app.post("/api/admin/pausar/{numero_wa}")
-     form_data = await request.form()
+ async def pausar_bot_manual(request: Request, numero_wa: str):
-     redirect_url = form_data.get("redirect", "/admin")
+     """Pausa al bot de forma manual para un WA específico."""
-     return RedirectResponse(url=redirect_url, status_code=303)
+     if not verificar_sesion(request):
- 
+         return RedirectResponse(url="/login", status_code=303)
- @app.post("/api/admin/pausar/{numero_wa}")
+ 
- async def pausar_bot_manual(request: Request, numero_wa: str):
+     if numero_wa in sesiones:
-     """Pausa al bot de forma manual para un WA específico."""
+         sesiones[numero_wa]["bot_activo"] = False
-     if not verificar_sesion(request):
+         sesiones[numero_wa]["escalado_en"] = datetime.utcnow()
-         re
… [diff truncated]

### 📐 Config/Infrastructure Conventions & Fixes
- **[convention] what-changed in .gitignore — confirmed 3x**: - 隧道_log.txt
+ 隧道_log.txt
- **[problem-fix] Fixed null crash in Sticker**: -                 texto = f'<div style="text-align:center;"><img src="/api/media/{media_id}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/150x150?text=Sticker\';"><br><small style="opacity:0.6;font-size:0.7rem;">Sticker</small></div>'
+                 src_url = media_id if media_id.startswith("http") else f"/api/media/{media_id}"
-             elif match_imagen:
+                 texto = f'<div style="text-align:center;"><img src="{src_url}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px;" alt="Sticker {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/150x150?text=Sticker\';"><br><small style="opacity:0.6;font-size:0.7rem;">Sticker</small></div>'
-                 media_id = match_imagen.group(1)
+             elif match_imagen:
-                 caption = match_imagen.group(2)
+                 media_id = match_imagen.group(1)
-                 img_tag = f'<img src="/api/media/{media_id}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/250x150?text=Imagen\';">'
+                 src_url = media_id if media_id.startswith("http") else f"/api/media/{media_id}"
-                 texto = img_tag + (f"<span>{caption}</span>" if caption else "")
+                 caption = match_imagen.group(2)
-                 
+                 img_tag = f'<img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src=\'https://placehold.co/250x150?text=Imagen\';">'
-             
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **[problem-fix] Fixed null crash in Parsear — protects against XSS and CSRF token theft**: -         enviar_mensaje(numero_wa, respuesta_final)
+         from whatsapp_client import enviar_mensaje, enviar_media
- 
+         
-     return respuesta_final
+         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
- 
+         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
- 
+         for p in partes:
- # ─────────────────────────────────────────────
+             p = p.strip()
- #  Panel de administración
+             if not p: continue
- # ─────────────────────────────────────────────
+             
- 
+             match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
- 
+             match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
- 
+             
- from fastapi import Response
+             if match_sticker: enviar_media(numero_wa, "sticker", match_sticker.group(1))
- 
+             elif match_img: enviar_media(numero_wa, "image", match_img.group(1))
- VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
+             else: enviar_mensaje(numero_wa, p)
- active_sessions = {}
+ 
- 
+     return respuesta_final
- def verificar_sesion(request: Request):
+ 
-     token = request.cookies.get("session_token")
+ 
-     return token in active_sessions
+ # ─────────────────────────────────────────────
- 
+ #  Panel de administración
- @app.get("/login", response_class=HTMLResponse)
+ # ─────────────────────────────────────────────
- async def login_get():
+ 
-     return obtener_login_html()
+ 
- @app.post("/login")
+ from fastapi import Response
- async def login_post(response: Response, username: str = Form(...), [REDACTED] = Form(...)):
+ 
-     if username in VALID_USERS and VALID_USERS[username] == [REDACTED] VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
-         import uuid
+ active_sessions = {}
-         token = str(uuid.uuid4())
+ 
-         active_sessions[token] = username
+ def verificar_sesion
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **[convention] Fixed null crash in FastAPI — confirmed 3x**: - from fastapi import FastAPI, Request, HTTPException, Form
+ from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
-     return HTMLResponse(html)
+     import glob
- 
+     pdfs_html = ""
- @app.post("/api/settings/save")
+     for pdf in glob.glob("*.pdf"):
- async def save_settings(request: Request, guia_content: str = Form(...)):
+         pdfs_html += f"<li class='pdf-list-item'><div style='display:flex;align-items:center;gap:0.5rem;'><svg class='icon-pdf' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/></svg> {pdf}</div> <button onclick=\"deletePdf('{pdf}')\" class='pdf-delete-btn'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M3 6h18'/><path d='M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6'/><path d='M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2'/></svg> Borrar</button></li>"
-     if not verificar_sesion(request):
+     
-         raise HTTPException(status_code=403, detail="No autorizado")
+     html = html.replace("{lista_pdfs}", pdfs_html or "<li style='color:var(--text-muted);font-style:italic;padding:0.5rem;'>Ningún archivo PDF subido.</li>")
- 
+     
-     with open("guia_respuestas.md", "w", encoding="utf-8") as f:
+     return HTMLResponse(html)
-         f.write(guia_content)
+ 
-         
+ @app.post("/api/settings/save")
-     # Limpiamos caché del bot nativo para que levante los nuevos conocimientos
+ async def save_settings(request: Request, guia_content: str = Form(...)):
-     import prompts
+     if not verificar_sesion(request):
-     prompts._GUIA_CACHE = ""
+         raise HTTPException(status_code=403, detail="No autorizado")
-     return RedirectResponse(url="/settings?saved=true", status_code=303)
+     with open("guia_respuestas.md", "w", encoding="utf-8") as f:
- 
+         f.write(guia_content)
- @app.get("/adm
… [diff truncated]
- **[problem-fix] Patched security issue RESPONSIVE**: -             <div class="container" style="gap:2rem;">
+         .container {
-                 
+             padding: 2.5rem;
-                 <div class="pdf-card" style="background:var(--accent-bg);border:1px solid var(--accent-border);border-radius:12px;padding:1.5rem;">
+             max-width: 1000px;
-                     <h3 style="margin-bottom:1rem;color:var(--text-main);font-family:var(--font-heading)">Documentos Complementarios (PDF)</h3>
+             margin: 0 auto;
-                     <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem">Estos archivos son leídos dinámicamente cada vez que un cliente te contacta.</p>
+             width: 100%;
-                     
+             display: flex;
-                     <ul style="list-style:none;margin-bottom:1.5rem;display:flex;flex-direction:column;gap:0.5rem;">
+             flex-direction: column;
-                         {lista_pdfs}
+             flex: 1;
-                     </ul>
+             gap: 2rem;
-                     
+         }
-                 </div>
+ 
- 
+         .editor-card {
-                 <div class="editor-card">
+             background-color: var(--accent-bg);
-                     <div class="editor-header">
+             border: 1px solid var(--accent-border);
-                         <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
+             border-radius: 12px;
-                         guia_respuestas.md
+             overflow: hidden;
-                     </div>
+             display: flex;
-                     <textarea class="code-editor" name="guia_content" spellcheck="false">{guia_content}</textarea>
+             flex-direction: column;
-                 </div>
+             flex: 1;
-
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Strengthened types Documentos**: -         .container {
+             <div class="container" style="gap:2rem;">
-             padding: 2.5rem;
+                 
-             max-width: 1000px;
+                 <div class="pdf-card" style="background:var(--accent-bg);border:1px solid var(--accent-border);border-radius:12px;padding:1.5rem;">
-             margin: 0 auto;
+                     <h3 style="margin-bottom:1rem;color:var(--text-main);font-family:var(--font-heading)">Documentos Complementarios (PDF)</h3>
-             width: 100%;
+                     <p style="color:var(--text-muted);font-size:0.85rem;margin-bottom:1rem">Estos archivos son leídos dinámicamente cada vez que un cliente te contacta.</p>
-             display: flex;
+                     
-             flex-direction: column;
+                     <ul style="list-style:none;margin-bottom:1.5rem;display:flex;flex-direction:column;gap:0.5rem;">
-             flex: 1;
+                         {lista_pdfs}
-         }
+                     </ul>
- 
+                     
-         .editor-card {
+                 </div>
-             background-color: var(--accent-bg);
+ 
-             border: 1px solid var(--accent-border);
+                 <div class="editor-card">
-             border-radius: 12px;
+                     <div class="editor-header">
-             overflow: hidden;
+                         <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
-             display: flex;
+                         guia_respuestas.md
-             flex-direction: column;
+                     </div>
-             flex: 1;
+                     <textarea class="code-editor" name="guia_content" spellcheck="false">{guia_content}</textarea>
-             min-height: 500px;
+                 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[decision] Optimized Cargar**: - from config import DOCUMENTOS_GUIA
+ from document_loader import cargar_multiples
- from document_loader import cargar_multiples
+ 
- 
+ # ── Cargar documentos UNA sola vez al llamar al prompt ────
- # ── Cargar documentos UNA sola vez al importar el módulo ────
+ # Así no se relee el disco cada vez que se procesa a menos que limpiemos el caché.
- # Así no se relee el disco cada vez que se actualiza el contexto del pedido.
+ _GUIA_CACHE: str = ""
- _GUIA_CACHE: str = ""
+ 
- 
+ def _obtener_guia() -> str:
- def _obtener_guia() -> str:
+     global _GUIA_CACHE
-     global _GUIA_CACHE
+     if not _GUIA_CACHE:
-     if not _GUIA_CACHE:
+         import glob
-         _GUIA_CACHE = cargar_multiples(DOCUMENTOS_GUIA)
+         docs = [{"ruta": "guia_respuestas.md", "etiqueta": "Guía de respuestas principal"}]
-     return _GUIA_CACHE
+         for pdf_file in glob.glob("*.pdf"):
- 
+             docs.append({"ruta": pdf_file, "etiqueta": pdf_file.replace(".pdf", "")})
- 
+         _GUIA_CACHE = cargar_multiples(docs)
- def get_system_prompt(datos_pedido: dict | None = None) -> str:
+     return _GUIA_CACHE
-     """
+ 
-     Construye el system prompt en 3 bloques:
+ 
-       1. Instrucciones base
+ def get_system_prompt(datos_pedido: dict | None = None) -> str:
-       2. Documentos de guía (cacheados en memoria)
+     """
-       3. Datos del pedido desde Firebase (si ya los tenemos)
+     Construye el system prompt en 3 bloques:
-     """
+       1. Instrucciones base
- 
+       2. Documentos de guía (cacheados en memoria)
-     # ── Bloque 1: instrucciones base ────────────────────────
+       3. Datos del pedido desde Firebase (si ya los tenemos)
-     prompt = """Eres María, la asistente virtual de atención al cliente de nuestra tienda.
+     """
- Tu canal de atención es WhatsApp exclusivamente.
+ 
- 
+     # ── Bloque 1: instrucciones base ────────────────────────
- REGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:
+     prompt = """Eres María, la asistente virtual de
… [diff truncated]
- **[what-changed] Added API key auth authentication**: - DOCUMENTOS_GUIA = [
+ import glob
-     {"ruta": "guia_respuestas.md", "etiqueta": "Guía de respuestas"},
+ DOCUMENTOS_GUIA = [{"ruta": "guia_respuestas.md", "etiqueta": "Guía de respuestas principal"}]
-     {"ruta": "FLUJO DE ATENCIÓN AL CLIENTE Y COBRANZA.pdf", "etiqueta": "Flujo de atención al cliente y cobranza"},
+ 
- ]
+ # Auto-descubrir cualquier PDF en la carpeta raíz
- 
+ for pdf_file in glob.glob("*.pdf"):
- # --- LM Studio (solo para bot_atc.py en consola) ---
+     DOCUMENTOS_GUIA.append({"ruta": pdf_file, "etiqueta": pdf_file.replace(".pdf", "")})
- LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
+ 
- LM_STUDIO_API_KEY  = "lm-studio"
+ # --- LM Studio (solo para bot_atc.py en consola) ---
- LM_STUDIO_MODEL    = "local-model"
+ LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
- 
+ LM_STUDIO_API_KEY  = "lm-studio"
- # --- Groq API (para server.py en producción) ---
+ LM_STUDIO_MODEL    = "local-model"
- GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
+ 
- GROQ_MODEL     = "llama-3.1-8b-instant"
+ # --- Groq API (para server.py en producción) ---
- 
+ GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
- # --- Parámetros del modelo ---
+ GROQ_MODEL     = "llama-3.1-8b-instant"
- TEMPERATURE = 0.05  # casi determinista: sigue los documentos sin inventar
+ 
- 
+ # --- Parámetros del modelo ---
- # --- Meta WhatsApp Business API ---
+ TEMPERATURE = 0.05  # casi determinista: sigue los documentos sin inventar
- META_ACCESS_TOKEN    = os.getenv("META_ACCESS_TOKEN", "")
+ 
- META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
+ # --- Meta WhatsApp Business API ---
- META_VERIFY_TOKEN    = os.getenv("META_VERIFY_TOKEN", "bot_atc_token")
+ META_ACCESS_TOKEN    = os.getenv("META_ACCESS_TOKEN", "")
- META_API_VERSION     = "v19.0"
+ META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
- 
+ META_VERIFY_TOKEN    = os.getenv("META_VERIFY_TOKEN", "bot_atc_token")
- # --- Firebase ---
+ META_API_VERSION     = "v19.0"
- FIREBASE_CREDENTIALS_PATH = "serviceAcc
… [diff truncated]
- **[what-changed] Replaced auth RedirectResponse**: -         raise HTTPException(status_code=403, detail="No autorizado")
+         return RedirectResponse(url="/login", status_code=303)
- **[what-changed] Replaced auth RedirectResponse**: -         raise HTTPException(status_code=403, detail="No autorizado")
+         return RedirectResponse(url="/login", status_code=303)
- **[convention] Fixed null crash in RedirectResponse — confirmed 3x**: -     return RedirectResponse(url=f"/admin", status_code=303)
+     return RedirectResponse(url=request.form().get("redirect", "/admin") if isinstance(request, Request) else "/admin", status_code=303)
- 
+ @app.post("/api/admin/pausar/{numero_wa}")
- @app.post("/api/admin/enviar_manual")
+ async def pausar_bot_manual(request: Request, numero_wa: str):
- async def enviar_manual_endpoint(request: Request):
+     """Pausa al bot de forma manual para un WA específico."""
-     """Recibe mensaje del panel web y lo despacha a WhatsApp nativamente."""
+     if not verificar_sesion(request):
-     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
-         raise HTTPException(status_code=403, detail="No autorizado")
+ 
-     
+     if numero_wa in sesiones:
-     data = await request.json()
+         sesiones[numero_wa]["bot_activo"] = False
-     wa_id = data.get("wa_id")
+         sesiones[numero_wa]["escalado_en"] = datetime.utcnow()
-     texto = data.get("texto", "").strip()
+         sesiones[numero_wa]["motivo_escalacion"] = "Intervención manual forzada"
-     
+         print(f"  [⏸ Bot pausado manualmente para {numero_wa}]")
-     if not wa_id or wa_id not in sesiones or not texto:
+         
-         return {"ok": False}
+     form_data = await request.form()
-         
+     redirect_url = form_data.get("redirect", f"/inbox/{numero_wa}")
-     s = sesiones[wa_id]
+     return RedirectResponse(url=redirect_url, status_code=303)
-     s["historial"].append({"role": "assistant", "content": texto})
+ 
-     s["ultima_actividad"] = datetime.utcnow()
+ 
-     
+ @app.post("/api/admin/enviar_manual")
-     print(f"  [👤 Humano -> {wa_id}]: {texto}")
+ async def enviar_manual_endpoint(request: Request):
-     
+     """Recibe mensaje del panel web y lo despacha a WhatsApp nativamente."""
-     # Send to WhatsApp
+     if not verificar_sesion(request):
-     from whatsapp_c
… [diff truncated]
- **[what-changed] what-changed in server.py**: -         <a href="/inbox/{num}&tab={tab}" class="chat-row {active_class}">
+         <a href="/inbox/{num}?tab={tab}" class="chat-row {active_class}">
-             <a href="/inbox&tab={tab}" class="btn-responsive-back" title="Volver a la lista">
+             <a href="/inbox?tab={tab}" class="btn-responsive-back" title="Volver a la lista">
- **[what-changed] what-changed in admin.html**: -         <!-- Agent Settings Icon (Futuro) -->
+         <!-- Agent Settings Icon -->
-         <a href="#" class="nav-item" title="Personalizar Agente IA (Próximamente)">
+         <a href="/settings" class="nav-item" title="Personalizar Agente IA">

📌 IDE AST Context: Modified symbols likely include [html]
