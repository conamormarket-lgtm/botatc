> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `guia_respuestas.md` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
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

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] what-changed in guia_respuestas.md**: - > "¡Ya tenemos todo validado! Tu pedido acaba de entrar a la cola de producción y muy pronto empezaremos a prepararlo. ⚙️"
+ > "¡Tu pedido ya está en etapa de preparación! Acaba de entrar a la cola de producción y pronto lo tendremos listo. ⚙️"
- > "Tu pedido ya está en producción, va bien encaminado. 🙌"
+ > "Tu pedido ya está en la etapa de preparación y va bien encaminado. 🙌"
- > "Hay una pequeña pausa porque uno de los productos tiene demora en stock. Ya lo estamos resolviendo. ¡Gracias por tu paciencia! 🙏"
+ > "Tu pedido se encuentra en la etapa de preparación, pero hay una pequeña pausa porque uno de los productos tiene demora de stock. Ya lo estamos resolviendo, ¡gracias por tu paciencia! 🙏"

📌 IDE AST Context: Modified symbols likely include [# Guía de Respuestas — Bot de Atención al Cliente]
- **[discovery] discovery in guia_respuestas.md**: - ## Estados del Pedido y Cómo Responder
+ ## Estados del Pedido y Cómo Responder (Usa EXACTAMENTE estas plantillas según el estado de DATOS DEL PEDIDO)
- ### 🎨 "En Diseño"
+ ### 🎨 "En Diseño" / "Diseño"
- > "¡Tu pedido está en diseño! 🎨 Nuestro equipo ya está trabajando en él."
+ > "¡Tu pedido está en diseño! 🎨 Nuestro equipo creativo ya está trabajando en él."
- ### ⚙️ "Preparación" / "En Preparación"
+ ### 💰 "En Cobranza" / "Cobranza"
- > "Tu pedido ya está en producción, va bien encaminado. 🙌"
+ > "Tu pedido está en proceso de cobranza y validación de pago. En breve avanzará a la siguiente etapa. 💳"
- ### 📦 "Empaquetado"
+ ### 📋 "Listo para Preparar"
- > "¡Ya está listo y lo estamos empaquetando! 📦 Pronto sale para despacho."
+ > "¡Ya tenemos todo validado! Tu pedido acaba de entrar a la cola de producción y muy pronto empezaremos a prepararlo. ⚙️"
- ### 🚚 "Enviado" / "En camino" / "Reparto"
+ ### ⚙️ "Preparación" / "En Preparación"
- > "¡Ya está en camino! 🚚 La agencia de envíos lo tiene a cargo."
+ > "Tu pedido ya está en producción, va bien encaminado. 🙌"
- ### ✅ "Entregado"
+ ### 📦 "Empaquetado" / "En Empaquetado"
- > "Según nuestros registros, tu pedido fue entregado. ¿Lo recibiste bien? 😊"
+ > "¡Ya está casi listo y en proceso de empaquetado! 📦 Muy pronto pasará al área de despachos."
- ### ⏸️ "En Pausa por Stock"
+ ### 🚚 "Enviado" / "En camino" / "En Reparto"
- > "Hay una pequeña pausa porque uno de los productos tiene demora en stock. Ya lo estamos resolviendo. ¡Gracias por tu paciencia! 🙏"
+ > "¡Ya está en camino! 🚚 La agencia o repartidor correspondiente lo tiene a cargo."
- ### ❌ "Anulado"
+ ### ✅ "Entregado"
- > "Veo que tu pedido fue anulado. Si quieres más info o hacer uno nuevo, cuéntame. 😊"
+ > "Según nuestros registros, tu pedido figura como entregado. ¿Lo recibiste bien? 😊"
- ---
+ ### 🏁 "Finalizado"
- 
+ > "Veo que tu pedido ya está totalmente finalizado y cerrado. ¡Espero que lo estés disfrutando mucho! 🎉"
- ## Situacio
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [# Guía de Respuestas — Bot de Atención al Cliente]
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
- **[convention] Strengthened types Contrase**: -         <label>Contraseña Administrativa</label>
+         <label>Contraseña</label>
-         <button type="submit">Desbloquear</button>
+         <button type="submit">Desbloquear el Sistema</button>
- **[what-changed] Added API route: /api/simulador/send**: -     </body>
+     </html>
-     </html>
+     """)
-     """.replace("__PWD__", pwd))
+ 
- 
+ @app.post("/api/simulador/send")
- @app.post("/api/simulador/send")
+ async def api_simular_mensaje(request: Request):
- async def api_simular_mensaje(request: Request):
+     """Recibe el mensaje falso del simulador y procesa la lógica nativa del webhook."""
-     """Recibe el mensaje falso del simulador y procesa la lógica nativa del webhook."""
+     try:
-     try:
+         data = await request.json()
-         data = await request.json()
+     except Exception:
-     except Exception:
+         raise HTTPException(status_code=400, detail="JSON inválido")
-         raise HTTPException(status_code=400, detail="JSON inválido")
+         
-         
+     if not verificar_sesion(request):
-     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
-         raise HTTPException(status_code=403, detail="No autorizado")
+ 
- 
+     numero = data.get("numero", "51999999991")
-     numero = data.get("numero", "51999999991")
+     nombre = data.get("nombre", "Tester")
-     nombre = data.get("nombre", "Tester")
+     texto = data.get("mensaje", "")
-     texto = data.get("mensaje", "")
+     
-     
+     print(f"\n{'─'*50}")
-     print(f"\n{'─'*50}")
+     print(f"🧪 SIMULADOR | {nombre} ({numero}): {texto}")
-     print(f"🧪 SIMULADOR | {nombre} ({numero}): {texto}")
+     
-     
+     respuesta = procesar_mensaje_interno(numero, nombre, texto, is_simulacion=True)
-     respuesta = procesar_mensaje_interno(numero, nombre, texto, is_simulacion=True)
+     
-     
+     return {"status": "ok", "respuesta": respuesta}
-     return {"status": "ok", "respuesta": respuesta}
+ 
- 
+ 
- 
