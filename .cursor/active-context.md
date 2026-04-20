> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `document_loader.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Added JWT tokens authentication — evolves the database schema to support new ...**: - 
+     provider: str | None = None
- @app.get("/api/admin/lines")
+     meta_phone_id: str | None = None
- async def api_list_lines(request: Request):
+     meta_token: str | None = None
-     if not verificar_sesion(request):
+ 
-         raise HTTPException(status_code=403, detail="No autorizado")
+ @app.get("/api/admin/lines")
-     import json
+ async def api_list_lines(request: Request):
-     import os
+     if not verificar_sesion(request):
-     aliases = {}
+         raise HTTPException(status_code=403, detail="No autorizado")
-     try:
+     import json
-         if os.path.exists("line_aliases.json"):
+     import os
-             with open("line_aliases.json", "r") as f:
+     aliases = {}
-                 aliases = json.load(f)
+     try:
-     except: pass
+         if os.path.exists("line_aliases.json"):
-     
+             with open("line_aliases.json", "r") as f:
-     if "principal" not in aliases:
+                 aliases = json.load(f)
-         aliases["principal"] = "Línea Principal Meta"
+     except: pass
-         
+     
-     from bot_manager import get_bot_for_line
+     if "principal" not in aliases:
-     lines_rich = {}
+         aliases["principal"] = {"name": "Línea Principal Meta"}
-     for lid, lname in aliases.items():
+         
-         # Protegemos frente a basura que se haya podido guardar en json
+     from bot_manager import get_bot_for_line
-         if isinstance(lname, dict):
+     lines_rich = {}
-             lname = lname.get("name", "undefined")
+     for lid, linfo in aliases.items():
- 
+         if isinstance(linfo, str):
-         lines_rich[lid] = {
+             linfo = {"name": linfo}  # Migration from old string format
-             "name": lname,
+             
-             "bot_id": get_bot_for_line(lid)
+         lname = linfo.get("name", "undefined")
-         }
+         provider = linfo.get("provider", "meta" if lid == "principal" else "")

… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Added JWT tokens authentication**: -             const div = documclass LineAliasPayload(BaseModel):
+             const div = document.createElement('div');
-     id: str
+             div.className = `msg msg-bot typing`;
-     name: str
+             div.id = id;
-     bot_id: str | None = None
+             div.innerText = 'escribiendo...';
-     provider: str | None = None
+             chat.appendChild(div);
-     meta_phone_id: str | None = None
+             scrollBottom();
-     meta_token: str | None = None
+         }
- 
+         
- @app.get("/api/admin/lines")
+         function removeTyping(id) {
- async def api_list_lines(request: Request):
+             const div = document.getElementById(id);
-     if not verificar_sesion(request):
+             if(div) div.remove();
-         raise HTTPException(status_code=403, detail="No autorizado")
+         }
-     import json
+         
-     import os
+         function scrollBottom() {
-     aliases = {}
+             chat.scrollTop = chat.scrollHeight;
-     try:
+         }
-         if os.path.exists("line_aliases.json"):
+       </script>
-             with open("line_aliases.json", "r") as f:
+     </html>
-                 aliases = json.load(f)
+     """)
-     except: pass
+ 
-     
+ @app.post("/api/simulador/send")
-     if "principal" not in aliases:
+ async def api_simular_mensaje(request: Request):
-         aliases["principal"] = {"name": "Línea Principal Meta"}
+     """Recibe el mensaje falso del simulador y procesa la lógica nativa del webhook."""
-         
+     try:
-     from bot_manager import get_bot_for_line
+         data = await request.json()
-     lines_rich = {}
+     except Exception:
-     for lid, linfo in aliases.items():
+         raise HTTPException(status_code=400, detail="JSON inválido")
-         if isinstance(linfo, str):
+         
-             linfo = {"name": linfo}  # Migration from old string format
+     if not verificar_sesion(request):
-
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] Added API route: /api/test_links**: - 
+ 
- @app.get('/api/test_links')
+ @app.get('/api/test_links')
- async def api_test_links(text: str = 'Prueba con https://www.instagram.com'):
+ async def api_test_links(text: str = 'Prueba con https://www.instagram.com'):
-     import re
+     import re
-     texto_renderizado = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
+     texto_renderizado = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
-     def linkify_text(match):
+     def linkify_text(match):
-         if match.group(1): return match.group(1)
+         if match.group(1): return match.group(1)
-         url = match.group(2)
+         url = match.group(2)
-         trailing = ''
+         trailing = ''
-         while url and url[-1] in '.,!?)':
+         while url and url[-1] in '.,!?)':
-             trailing = url[-1] + trailing
+             trailing = url[-1] + trailing
-             url = url[:-1]
+             url = url[:-1]
-         href = url if url.startswith('http') else 'http://' + url
+         href = url if url.startswith('http') else 'http://' + url
-         return f'<a href="{href}" target="_blank">{url}</a>{trailing}'
+         return f'<a href="{href}" target="_blank">{url}</a>{trailing}'
-     texto_renderizado = re.sub(r'(<[^>]+>)|((?:https?://|www\.|wa\.me/)[^\s<>]+|[a-zA-Z0-9_-]+\.[a-zA-Z]{2,5}(?:/[^\s<>]*)?)', linkify_text, texto_renderizado)
+     texto_renderizado = re.sub(r'(<[^>]+>)|((?:https?://|www\.|wa\.me/)[^\s<>]+|[a-zA-Z0-9_-]+\.[a-zA-Z]{2,5}(?:/[^\s<>]*)?)', linkify_text, texto_renderizado)

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] Added API route: /api/test_links**: + @app.get('/api/test_links')
+ async def api_test_links(text: str = 'Prueba con https://www.instagram.com'):
+     import re
+     texto_renderizado = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
+     def linkify_text(match):
+         if match.group(1): return match.group(1)
+         url = match.group(2)
+         trailing = ''
+         while url and url[-1] in '.,!?)':
+             trailing = url[-1] + trailing
+             url = url[:-1]
+         href = url if url.startswith('http') else 'http://' + url
+         return f'<a href="{href}" target="_blank">{url}</a>{trailing}'
+     texto_renderizado = re.sub(r'(<[^>]+>)|((?:https?://|www\.|wa\.me/)[^\s<>]+|[a-zA-Z0-9_-]+\.[a-zA-Z]{2,5}(?:/[^\s<>]*)?)', linkify_text, texto_renderizado)
+     return {'original': text, 'resultado': texto_renderizado}
+ 

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] what-changed in trace_texto.txt**: File updated (external): trace_texto.txt

Content summary (120 lines):
��
- **[what-changed] what-changed in test_regex.py**: File updated (external): test_regex.py

Content summary (7 lines):
import re
text='Ver https://google.com y www.bing.com'
def l(m):
  if m.group(1): return m.group(1)
  return m.group(2)
print(re.sub(r'(<[^>]+>)|(https?://[^\s<>]+|www\.[^\s<>]+)', l, text))

- **[convention] what-changed in dump.html — confirmed 3x**: File updated (external): dump.html

Content summary (815 lines):
��
- **[what-changed] what-changed in guia_respuestas.md**: - - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/gracias%20por%20tu%20compa.webp]  -> (Usa este al despedirte luego de que el cliente confirma que est� conforme con su compra)
+ - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/gracias%20por%20tu%20compa.webp]  -> (Usa este al despedirte luego de que el cliente confirma que está conforme con su compra)
- - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/hola.webp]  -> (Usa este si el cliente saluda durante la ma�ana)
+ - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/hola.webp]  -> (Usa este si el cliente saluda durante la mañana)
- - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/quedo%20atento.webp]  -> (Usa este cuando queda algo pendiente al finalizar la conversaci�n)
+ - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/quedo%20atento.webp]  -> (Usa este cuando queda algo pendiente al finalizar la conversación)
- - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/un%20minuto.webp]  -> (Usa este cuando escalas la conversacion a un humano)
+ - [sticker:https://raw.githubusercontent.com/conamormarket-lgtm/botatc/refs/heads/main/stickers/un%20minuto.webp]  -> (Usa este cuando escalas la conversación a un humano)

📌 IDE AST Context: Modified symbols likely include [# Guía de Respuestas — Bot de Atención al Cliente]
- **[what-changed] what-changed in guia_respuestas.md**: - Tienes un pequeño catálogo de stickers oficiales para ser m�s din�mica.
+ Tienes un pequeño catálogo de stickers oficiales para ser más dinámica.
- EST� ESTRICTAMENTE PROHIBIDO inventar URLs o usar im�genes que no est�n en esta lista.
+ ESTÁ ESTRICTAMENTE PROHIBIDO inventar URLs o usar imágenes que no estén en esta lista.
- Para usarlos, copia y pega EXACTAMENTE la etiqueta a continuaci�n al final de tu respuesta:
+ Para usarlos, copia y pega EXACTAMENTE la etiqueta a continuación al final de tu respuesta:

📌 IDE AST Context: Modified symbols likely include [# Guía de Respuestas — Bot de Atención al Cliente]
- **[convention] what-changed in guia_respuestas.md — confirmed 4x**: - Tienes un pequeño cat�logo de stickers oficiales para ser m�s din�mica.
+ Tienes un pequeño catálogo de stickers oficiales para ser m�s din�mica.

📌 IDE AST Context: Modified symbols likely include [# Guía de Respuestas — Bot de Atención al Cliente]
- **[convention] problem-fix in server.py — confirmed 3x**: -         line_alias = aliases.get(ch_line, "Línea Secundaria" if ch_line != "principal" else "")
+         line_alias = parsed_aliases.get(ch_line, "Línea Secundaria" if ch_line != "principal" else "")

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] Added JWT tokens authentication — confirmed 6x**: -     headers = {
+     meta_token, meta_phone_id, meta_api_url = _get_meta_credentials(line_id)
-         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
+ 
-         "Content-Type": "application/json",
+     headers = {
-     }
+         "Authorization": f"Bearer {meta_token}",
-     payload = {
+         "Content-Type": "application/json",
-         "messaging_product": "whatsapp",
+     }
-         "recipient_type": "individual",
+     payload = {
-         "to": numero_destino,
+         "messaging_product": "whatsapp",
-         "type": "text",
+         "recipient_type": "individual",
-         "text": {"body": texto},
+         "to": numero_destino,
-     }
+         "type": "text",
-     try:
+         "text": {"body": texto},
-         async with httpx.AsyncClient() as client:
+     }
-             response = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
+     try:
-             response.raise_for_status()
+         async with httpx.AsyncClient() as client:
-             print(f"[OK] Mensaje manual enviado a {numero_destino}")
+             response = await client.post(meta_api_url, headers=headers, json=payload, timeout=10)
-             return response.json().get("messages", [{}])[0].get("id")
+             response.raise_for_status()
-     except httpx.HTTPStatusError as e:
+             print(f"[OK] Mensaje manual enviado a {numero_destino}")
-         print(f"[ERROR] Error Meta API al enviar manual ({e.response.status_code}): {e.response.text}")
+             return response.json().get("messages", [{}])[0].get("id")
-         return None
+     except httpx.HTTPStatusError as e:
-     except Exception as e:
+         print(f"[ERROR] Error Meta API al enviar manual ({e.response.status_code}): {e.response.text}")
-         print(f"[ERROR] Error enviando mensaje manual: {e}")
+         return None
-         return None
+     except Exception as e:
- 
+         print(f"[ERROR] Erro
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [_get_line_id, _get_meta_credentials, enviar_mensaje, enviar_media, enviar_mensaje_texto]
- **[what-changed] Updated configuration Eres — externalizes configuration for environment flexi...**: -         return {
+         prompt_base = "Eres María, la asistente virtual de Wala..."
-             "bots": {
+         try:
-                 "bot_wala": {
+             if os.path.exists('guia_respuestas.md'):
-                     "name": "Wala Principal",
+                 with open('guia_respuestas.md', 'r', encoding='utf-8') as mf:
-                     "is_active": True,
+                     prompt_base = mf.read()
-                     "prompt": "Eres María, la asistente virtual de Wala..."
+         except:
-                 }
+             pass
-             },
+             
-             "lines_mapping": {
+         default_data = {
-                 "principal": "bot_wala"
+             "bots": {
-             }
+                 "bot_wala": {
-         }
+                     "name": "Wala Principal",
-     with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
+                     "is_active": True,
-         return json.load(f)
+                     "prompt": prompt_base
- 
+                 }
- def _save_config(data):
+             },
-     with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
+             "lines_mapping": {
-         json.dump(data, f, ensure_ascii=False, indent=4)
+                 "principal": "bot_wala"
- 
+             }
- def get_bot_for_line(line_id: str) -> str | None:
+         }
-     """Devuelve el ID del bot asignado a una línea, o None si atiende un humano."""
+         with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
-     config = _load_config()
+             json.dump(default_data, f, ensure_ascii=False, indent=4)
-     return config.get("lines_mapping", {}).get(line_id)
+         return default_data
- 
+         
- def set_bot_for_line(line_id: str, bot_id: str | None):
+     with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
-     config = _load_config()
+         return json.load(f)
-     if "lines_mapping" not in config:
+ 
-         config["lines_mapping"] = {}
+ def _save_config(data):
-     config["lines_
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [CONFIG_FILE, _load_config, _save_config, get_bot_for_line, set_bot_for_line]
- **[what-changed] what-changed in prompts.py**: - 11. Cuando se le indique al cliente por primera vez en la sesión (cuéntese sesión como cada vez que tienes que saludar nuevamente al cliente) el estado de su pedido también recordarle que puede verificar el estado de su pedido en la página hhttps://wala-two.vercel.app/pedidos e informar que ahí encontrará la misma información que le brindarás tú.
+ 11. Cuando se le indique al cliente por primera vez en la sesión (cuéntese sesión como cada vez que tienes que saludar nuevamente al cliente) el estado de su pedido también recordarle que puede verificar el estado de su pedido en la página https://wala-two.vercel.app/pedidos e informar que ahí encontrará la misma información que le brindarás tú.

📌 IDE AST Context: Modified symbols likely include [_GUIA_CACHE, _obtener_guia, get_system_prompt, MENSAJE_BIENVENIDA]
- **[convention] Patched security issue Creamos — protects against XSS and CSRF token theft — confirmed 3x**: -     # Reemplazamos el texto original (raw) con el normalizado para Gemini
+     # Creamos la copia para Gemini SIN alterar el historial persistente para que en el UI sigan las burbujas separadas.
-     if sesion["historial"] and sesion["historial"][-1]["role"] == "user":
+     historial_para_gemini = recortar_historial(sesion["historial"])
-         sesion["historial"][-1]["content"] = texto_modelo
+     if historial_para_gemini and historial_para_gemini[-1]["role"] == "user":
-         
+         # Usamos texto_modelo que concatena todo con ' | ' para que la IA entienda el contexto fusionado
-     historial_para_gemini = recortar_historial(sesion["historial"])
+         historial_para_gemini[-1]["content"] = texto_modelo
-     print(f"  [🧠 Enviando {len(historial_para_gemini)} turnos a Gemini]")
+         
-     respuesta_bot = llamar_gemini(historial_para_gemini)
+     print(f"  [🧠 Enviando {len(historial_para_gemini)} turnos a Gemini]")
-     
+     respuesta_bot = llamar_gemini(historial_para_gemini)
-     if not respuesta_bot.strip():
+     
-         # Falla silenciosamente si Gemini no genera respuesta útil o tira error
+     if not respuesta_bot.strip():
-         print("  [[ERROR] Respuesta vacía de Gemini. Ignorando...]")
+         # Falla silenciosamente si Gemini no genera respuesta útil o tira error
-         return None
+         print("  [[ERROR] Respuesta vacía de Gemini. Ignorando...]")
- 
+         return None
-     # ── Procesar escalación si el modelo la detectó ───────
+ 
-     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
+     # ── Procesar escalación si el modelo la detectó ───────
- 
+     respuesta_final = procesar_escalacion(numero_wa, sesion, respuesta_bot)
-     # ── Enviar respuesta al cliente por WhatsApp ──────────
+ 
-     print(f"🤖 María: {respuesta_final[:80]}...")
+     # ── Enviar respuesta al cliente por WhatsApp ──────────
-     wamid_out = None
+     print(f"���
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
