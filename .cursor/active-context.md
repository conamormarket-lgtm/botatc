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

### 📐 Config/Infrastructure Conventions & Fixes
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
- **[decision] Optimized Prevenir**: -     # deudaTotal podría no existir, asumimos 0 por defecto o extraemos de donde debe ser
+     try: deuda_nueva = float(pedido.get("deudaTotal", 0))
-     try:
+     except: deuda_nueva = 0
-         deuda_nueva = float(pedido.get("deudaTotal", 0))
+         
-     except:
+     estado_viejo = cache_pedidos.get(doc_id, {}).get("estadoGeneral", "")
-         deuda_nueva = 0
+     deuda_vieja = cache_pedidos.get(doc_id, {}).get("deudaTotal", -1)
-         
+     
-     estado_viejo = cache_pedidos.get(doc_id, {}).get("estadoGeneral", "")
+     # Prevenir alertas al cargar por primera vez un documento modificado
-     deuda_vieja = cache_pedidos.get(doc_id, {}).get("deudaTotal", -1)
+     if not estado_viejo or deuda_vieja == -1:
-     
+         return
-     # Ignorar si es el mismo estado y misma deuda
+ 
-     if estado_nuevo == estado_viejo and deuda_nueva == deuda_vieja:
+     # Escenario 1: Acaba de pagar su deuda al 100% Y se encuentra en Preparación
-         return
+     # (Puede haber llegado a Preparación en este instante, o ya estar allí y recién pagar)
- 
+     if estado_nuevo == "Preparación" and deuda_nueva == 0 and deuda_vieja > 0:
-     # Escenario 1: Pagó al 100% (deuda bajó a 0) Y pasó a Preparación
+         _enviar_plantilla_1(pedido)
-     if estado_nuevo == "Preparación" and deuda_nueva == 0 and deuda_vieja > 0:
+         return
-         _enviar_plantilla_1(pedido)
+ 
-     
+     # Escenario 2: Cambio hacia una etapa posterior en estadoGeneral
-     # Escenario 2: Cambio de etapa normal hacia un estado MAYOR
+     if estado_nuevo != estado_viejo:
-     elif estado_nuevo != estado_viejo:
+         peso_nuevo = ORDEN_ETAPAS.get(estado_nuevo, 0)
-         peso_nuevo = ORDEN_ETAPAS.get(estado_nuevo, 0)
+         peso_viejo = ORDEN_ETAPAS.get(estado_viejo, 0)
-         peso_viejo = ORDEN_ETAPAS.get(estado_viejo, 0)
+         
-         
+         # Si avanza y es mayor que Diseño
-             # Excluimos "Preparación" si acaba de pasar de (deuda_
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [ORDEN_ETAPAS, cache_pedidos, notificar_whatsapp, _enviar_plantilla_1, _enviar_plantilla_2]
- **[trade-off] trade-off in prompts.py**: -         prompt += "\n--- DATOS DE LOS PEDIDOS DEL CLIENTE (información real en tiempo real) ---\n"
+         prompt += "\n--- DATOS DE LOS PEDIDOS DEL CLIENTE (información real del sistema) ---\n"
-         from firebase_client import calcular_cola_pedido
+         for i, pedido in enumerate(datos_pedido):
-         
+             nombre    = f"{pedido.get('clienteNombre', '')} {pedido.get('clienteApellidos', '')}".strip()
-         for i, pedido in enumerate(datos_pedido):
+             estado    = pedido.get("estadoGeneral", "No disponible")
-             nombre    = f"{pedido.get('clienteNombre', '')} {pedido.get('clienteApellidos', '')}".strip()
+             id_pedido = pedido.get("id", "N/A")
-             estado    = pedido.get("estadoGeneral", "No disponible")
+             
-             id_pedido = pedido.get("id", "N/A")
+             prompt += f"Pedido {i+1}:\n"
-             
+             prompt += f"- Nombre del cliente : {nombre}\n"
-             # Nuevos datos (Provincia, Deuda, Puesto)
+             prompt += f"- N° de pedido       : {id_pedido}\n"
-             provincia = pedido.get("clienteProvincia", "No especificada").strip()
+             prompt += f"- Estado actual      : {estado}\n\n"
-             
+         prompt += "--- FIN DE DATOS ---\n"
-             # Finanzas (deuda) -> Revisar el dict 'cobro'
+         prompt += "IMPORTANTE: Si el cliente consulta sobre su pedido y tiene más de uno, pregúntale amable y explícitamente sobre cuál de los pedidos mencionados necesita ayuda, dándole los detalles por ID o producto.\n"
-             cobro = pedido.get("cobro", {})
+     else:
-             restante = cobro.get("restante", -1)
+         prompt += """
-             if restante == 0:
+ --- DATOS DEL PEDIDO ---
-                 finanzas = "Pagado al 100% (Deuda cero)"
+ Aún no tienes datos de ningún pedido específico.
-             elif restante > 0:
+ Solo pide el identificador si el cliente pregunta por SU pedido en particular.
-       
… [diff truncated]
- **[problem-fix] problem-fix in firebase_client.py**: - def calcular_cola_pedido(pedido: dict) -> int:
-     """
-     Calcula el puesto exacto de un pedido comparando cuántos IDs 
-     (secuencias más antiguas) existen en la misma etapa (estadoGeneral).
-     """
-     estado = pedido.get("estadoGeneral")
-     pid = pedido.get("id")
-     if not estado or not pid: return 0
-     
-     db = inicializar_firebase()
-     try:
-         docs = db.collection(COLECCION_PEDIDOS).where(filter=FieldFilter("estadoGeneral", "==", estado)).get()
-         puesto = 1
-         for d in docs:
-             data = d.to_dict()
-             other_id = data.get("id", "")
-             if other_id and other_id < pid:
-                 puesto += 1
-         return puesto
-     except Exception as e:
-         print(f"Error cola: {e}")
-         return 0
- 

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id]
- **[what-changed] Replaced auth server**: -             max_output_tokens=300,
+             max_output_tokens=800,

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, sesiones, BOT_GLOBAL_ACTIVO, mensajes_pendientes]
- **[convention] Fixed null crash in Mapeamos — protects against XSS and CSRF token theft — confirmed 4x**: -         # Mapeamos el historial resto a formato Gemini
+         # Mapeamos el historialresto a formato Gemini, uniendo roles consecutivos si los hay
-             gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
+             
-             
+             # Si el último mensaje es del mismo rol, simplemente anexamos el texto para no romper la regla
-         config = types.GenerateContentConfig(
+             if gemini_contents and gemini_contents[-1]["role"] == role:
-             system_instruction=system_text,
+                 gemini_contents[-1]["parts"][0]["text"] += f"\n\n{msg['content']}"
-             temperature=TEMPERATURE,
+             else:
-             max_output_tokens=300,
+                 gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
-         )
+             
-         
+         config = types.GenerateContentConfig(
-         response = gemini_client.models.generate_content(
+             system_instruction=system_text,
-             model=GEMINI_MODEL,
+             temperature=TEMPERATURE,
-             contents=gemini_contents,
+             max_output_tokens=300,
-             config=config,
+         )
-         )
+         
-         return response.text.strip()
+         response = gemini_client.models.generate_content(
-     except Exception as e:
+             model=GEMINI_MODEL,
-         import traceback
+             contents=gemini_contents,
-         with open("error_gemini.txt", "w") as f:
+             config=config,
-             f.write(traceback.format_exc())
+         )
-         print(f"❌ Error Gemini: {e}")
+         return response.text.strip()
-         return "Disculpa, tuve un problema técnico. Intenta en un momento. 🙏"
+     except Exception as e:
- 
+         import traceback
- 
+         with open("error_gemini.txt", "w") as f:
- def recortar_historial(historial: list[dict]) -> list[dict]:
+             f.writ
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
