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
- **[problem-fix] Fixed null crash in Procesar — protects against XSS and CSRF token theft**: -     try:
+     respuesta_bot = llamar_gemini(sesion["historial"])
-         respuesta_bot = llamar_gemini(sesion["historial"])
+ 
- 
+     # ── Procesar escalación si el modelo la detectó ───────
-     # ── Procesar escalación si el modelo la detectó ───────
+     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
-     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
+ 
- 
+     # ── Guardar respuesta en historial ────────────────────
-     # ── Guardar respuesta en historial ────────────────────
+     sesion["historial"].append({"role": "assistant", "content": respuesta_final})
-     sesion["historial"].append({"role": "assistant", "content": respuesta_final})
+ 
- 
+     # ── Enviar respuesta al cliente por WhatsApp ──────────
-     # ── Enviar respuesta al cliente por WhatsApp ──────────
+     print(f"🤖 María: {respuesta_final[:80]}...")
-     print(f"🤖 María: {respuesta_final[:80]}...")
+     if not is_simulacion:
-     if not is_simulacion:
+         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
-         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
+         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
-         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
+         for p in partes:
-         for p in partes:
+             p = p.strip()
-             p = p.strip()
+             if not p: continue
-             if not p: continue
+             
-             
+             match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
-             match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
+             match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
-             match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
+             
-             
+             if match_sticker: enviar_media(numero_wa, "sticker", match_sticker.group(1))
-             if match_stick
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, sesiones, BOT_GLOBAL_ACTIVO, mensajes_pendientes]
- **[problem-fix] problem-fix in test_groq.py**: File updated (external): test_groq.py

Content summary (10 lines):
﻿from dotenv import load_dotenv
load_dotenv()
import os, groq
client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
try:
  resp = client.chat.completions.create(model='llama3-8b-8192', messages=[{'role': 'user', 'content': 'hola'}], max_tokens=10)
  print('OK:', resp.choices[0].message.content)
except Exception as e:
  print('ERROR:', e)

- **[problem-fix] Fixed null crash in Parsear — protects against XSS and CSRF token theft**: -         from whatsapp_client import enviar_mensaje, enviar_media
+         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
-         
+         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
-         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
+         for p in partes:
-         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
+             p = p.strip()
-         for p in partes:
+             if not p: continue
-             p = p.strip()
+             
-             if not p: continue
+             match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
-             
+             match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
-             match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
+             
-             match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
+             if match_sticker: enviar_media(numero_wa, "sticker", match_sticker.group(1))
-             
+             elif match_img: enviar_media(numero_wa, "image", match_img.group(1))
-             if match_sticker: enviar_media(numero_wa, "sticker", match_sticker.group(1))
+             else: enviar_mensaje(numero_wa, p)
-             elif match_img: enviar_media(numero_wa, "image", match_img.group(1))
+ 
-             else: enviar_mensaje(numero_wa, p)
+     return respuesta_final
-     return respuesta_final
+ 
- 
+ # ─────────────────────────────────────────────
- 
+ #  Panel de administración
- #  Panel de administración
+ 
- # ─────────────────────────────────────────────
+ 
- 
+ from fastapi import Response
- from fastapi import Response
+ VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
- 
+ active_sessions = {}
- VALID_USERS = {"admin": ADMIN_PASSWORD, "operador": "operadorATC2026"}
+ 
- active_sessions = {}
+ def verificar_sesion(request: Request):
- 
+     token = request.cookies.get("session_token")
- d
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **[what-changed] Replaced dependency server**: -     from whatsapp_client import enviar_mensaje_texto, enviar_media
+     from whatsapp_client import enviar_mensaje, enviar_media
-             else: await enviar_mensaje_texto(wa_id, p)
+             else: enviar_mensaje(wa_id, p)

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **[convention] Fixed null crash in Procesar — protects against XSS and CSRF token theft — confirmed 3x**: -     sesion["historial"].append({"role": "user", "content": texto_modelo})
+     if sesion["historial"] and sesion["historial"][-1]["role"] == "user":
-     sesion["historial"] = recortar_historial(sesion["historial"])
+         sesion["historial"][-1]["content"] = texto_modelo
- 
+     else:
-     respuesta_bot = llamar_groq(sesion["historial"])
+         sesion["historial"].append({"role": "user", "content": texto_modelo})
- 
+         
-     # ── Procesar escalación si el modelo la detectó ───────
+     sesion["historial"] = recortar_historial(sesion["historial"])
-     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
+ 
- 
+     respuesta_bot = llamar_groq(sesion["historial"])
-     # ── Guardar respuesta en historial ────────────────────
+ 
-     sesion["historial"].append({"role": "assistant", "content": respuesta_final})
+     # ── Procesar escalación si el modelo la detectó ───────
- 
+     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
-     # ── Enviar respuesta al cliente por WhatsApp ──────────
+ 
-     print(f"🤖 María: {respuesta_final[:80]}...")
+     # ── Guardar respuesta en historial ────────────────────
-     if not is_simulacion:
+     sesion["historial"].append({"role": "assistant", "content": respuesta_final})
-         from whatsapp_client import enviar_mensaje, enviar_media
+ 
-         
+     # ── Enviar respuesta al cliente por WhatsApp ──────────
-         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
+     print(f"🤖 María: {respuesta_final[:80]}...")
-         partes = re.split(r'(\[sticker:[^\]]+\]|\[imagen:[^\]]+\])', respuesta_final)
+     if not is_simulacion:
-         for p in partes:
+         from whatsapp_client import enviar_mensaje, enviar_media
-             p = p.strip()
+         
-             if not p: continue
+         # Parsear si el bot incluyó etiquetas [sticker:...], [imagen:...]
-             
+         p
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, groq_client, sesiones, BOT_GLOBAL_ACTIVO, REGEX_ESCALAR]
- **[convention] what-changed in .gitignore — confirmed 3x**: - 隧道_log.txt
+ 隧道_log.txt
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
