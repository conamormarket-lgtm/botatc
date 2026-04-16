> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `admin.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Patched security issue Client — protects against XSS and CSRF token theft**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- import subprocess
+ import subprocess
- import os
+ import os
- node_qr_process = None
+ node_qr_process = None
- 
+ 
- @app.on_event('startup')
+ @app.on_event('startup')
- def start_node_service():
+ def start_node_service():
-     global node_qr_process
+     global node_qr_process
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-     if os.path.exists(qr_dir):
+     if os.path.exists(qr_dir):
-         try:
+         try:
-             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
+             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
-             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=open('static/node_log.txt', 'w'), stderr=open('static/node_err.txt', 'w'))
+             node_exe = 'node'
-         except Exception as e:
+             # --- Auto-descubridor/Instalador de Node.js portable ---
-             print('? Error al iniciar Node:', e)
+             import platform
-             with open('static/node_status.txt', 'w') as f:
+             if platform.system() == 'Linux':
-                 f.write(f'PYTHON EXCEPTION:\\n{e}')
+                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
- 
+                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
- @app.on_event('shutdown')
+                 if not os.path.exists(node_portable_exe):
- def stop_node_service():
+                     try:
-     global node_qr_process
+                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
-     if node_qr_process:
+                     except (FileNotFoundError, Exception):
-         try: node_qr_process.terminate()
+      
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **⚠️ GOTCHA: Patched security issue Client — protects against XSS and CSRF token theft**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- @app.on_event("startup")
+ node_qr_process = None
- def startup_event():
+ 
-     # ── Restaurar toda la memoria y stickers desde Firebase ──
+ @app.on_event('startup')
-     try:
+ def start_node_service():
-         from firebase_client import cargar_todas_las_sesiones
+     global node_qr_process
-         # Restaurar sesiones (Inbox)
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-         sesiones_restauradas = cargar_todas_las_sesiones()
+     if os.path.exists(qr_dir):
-         for wa_id, s in sesiones_restauradas.items():
+         try:
-             sesiones[wa_id] = s
+             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
-         print(f"[OK] Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
+             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
-         
+         except Exception as e:
-         # Stickers are now loaded on-demand via Serverless Endpoints.
+             print('? Error al iniciar Node:', e)
-         
+ 
-         # Restaurar Etiquetas
+ @app.on_event('shutdown')
-         from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
+ def stop_node_service():
-         global global_labels, global_groups
+     global node_qr_process
-         global_labels = cargar_etiquetas_bd()
+     if node_qr_process:
-         print(f"[OK] Se restauraron {len(global_labels)} etiquetas globales.")
+         try: node_qr_process.terminate()
-         global_groups = cargar_grupos_bd()
+         except: pass
-         print(f"[OK] Se restauraron {len(global_groups)} grupos virtuales.")
+ 
-     except Exception as e:
+ @app.on_event("startup")
-         print(f"[ERROR] Error al restaurar datos desde Firebase: {e}")
+ def startup_event(
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **⚠️ GOTCHA: Updated firebase_client database schema**: -     num_norm = normalizar_numero(payload.wa_id)
+     # Meta siempre entrega mensajes con código de país completo (ej: "51997778512").
-     obtener_o_crear_sesion(num_norm)
+     # Usamos ese mismo formato como clave de sesión para que coincida.
-     return {"ok": True, "wa_id": num_norm}
+     digitos = payload.wa_id.replace("+", "").replace(" ", "").strip()
- 
+     # Si son 9 dígitos peruanos sin código de país, agregar 51
- class LabelPayload(BaseModel):
+     if len(digitos) == 9 and not digitos.startswith("51"):
-     id: str
+         digitos = "51" + digitos
-     name: Optional[str] = None
+     obtener_o_crear_sesion(digitos)
-     color: Optional[str] = None
+     return {"ok": True, "wa_id": digitos}
- @app.post("/api/admin/labels/save")
+ class LabelPayload(BaseModel):
- async def api_save_label(payload: LabelPayload, request: Request):
+     id: str
-     if not verificar_sesion(request):
+     name: Optional[str] = None
-         raise HTTPException(status_code=403, detail="No autorizado")
+     color: Optional[str] = None
-     if not es_admin(request):
+ 
-         raise HTTPException(status_code=403, detail="Solo administradores")
+ @app.post("/api/admin/labels/save")
-     from firebase_client import guardar_etiqueta_bd
+ async def api_save_label(payload: LabelPayload, request: Request):
-     guardar_etiqueta_bd(payload.id, payload.name, payload.color)
+     if not verificar_sesion(request):
-     global global_labels
+         raise HTTPException(status_code=403, detail="No autorizado")
-     global_labels = [l for l in global_labels if l.get("id") != payload.id]
+     if not es_admin(request):
-     global_labels.append({"id": payload.id, "name": payload.name, "color": payload.color})
+         raise HTTPException(status_code=403, detail="Solo administradores")
-     return {"ok": True}
+     from firebase_client import guardar_etiqueta_bd
- 
+     guardar_etiqueta_bd(payload.id, payload.name, payloa
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] what-changed in whatsapp_client.py**: -         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
+         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
-         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
+         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
- 
+ 
+ 
- **[what-changed] Refactored Client logic**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- import threading
+ import threading
- import subprocess
+ import subprocess
- import os
+ import os
- node_qr_process = None
+ node_qr_process = None
- 
+ 
- def _run_node_magic():
+ def _run_node_magic():
-     global node_qr_process
+     global node_qr_process
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-     if os.path.exists(qr_dir):
+     if os.path.exists(qr_dir):
-         try:
+         try:
-             node_exe = 'node'
+             node_exe = 'node'
-             import platform
+             import platform
-             if platform.system() == 'Linux':
+             if platform.system() == 'Linux':
-                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
+                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
-                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
+                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
-                 if not os.path.exists(node_portable_exe):
+                 if not os.path.exists(node_portable_exe):
-                     try:
+                     try:
-                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
+                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
-                     except (FileNotFoundError, Exception):
+                     except (FileNotFoundError, Exception):
-                         import urllib.request, tarfile
+                         import urllib.request, tarfile
-                         tar_path = os.path.join(os.path.dirname(__file__), 'node.tar.gz')
+            
… [diff truncated]
- **[problem-fix] Patched security issue Client — protects against XSS and CSRF token theft**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- @app.on_event("startup")
+ import threading
- def startup_event():
+ import subprocess
-     # ── Restaurar toda la memoria y stickers desde Firebase ──
+ import os
-     try:
+ node_qr_process = None
-         from firebase_client import cargar_todas_las_sesiones
+ 
-         # Restaurar sesiones (Inbox)
+ def _run_node_magic():
-         sesiones_restauradas = cargar_todas_las_sesiones()
+     global node_qr_process
-         for wa_id, s in sesiones_restauradas.items():
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-             sesiones[wa_id] = s
+     if os.path.exists(qr_dir):
-         print(f"[OK] Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
+         try:
-         
+             node_exe = 'node'
-         # Stickers are now loaded on-demand via Serverless Endpoints.
+             import platform
-         
+             if platform.system() == 'Linux':
-         # Restaurar Etiquetas
+                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
-         from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
+                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
-         global global_labels, global_groups
+                 if not os.path.exists(node_portable_exe):
-         global_labels = cargar_etiquetas_bd()
+                     try:
-         print(f"[OK] Se restauraron {len(global_labels)} etiquetas globales.")
+                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
-         global_groups = cargar_grupos_bd()
+                     except (FileNotFoundError, Exception):
-         print(f"[OK] Se restauraron {len(global_groups)} grupos virtuales.")
+                         import urllib.request, 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **[problem-fix] problem-fix in server.py**: - 
+ 
+ 

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] what-changed in whatsapp_client.py — confirmed 3x**: -         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
+         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
-         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/send", 
+         req = urllib.request.Request("http://localhost:3000/api/qr/send", 
- 
+ 
- 
- **[convention] Patched security issue Restaurar — protects against XSS and CSRF token theft — confirmed 4x**: - import subprocess
+ @app.on_event("startup")
- import os
+ def startup_event():
- node_qr_process = None
+     # ── Restaurar toda la memoria y stickers desde Firebase ──
- 
+     try:
- @app.on_event('startup')
+         from firebase_client import cargar_todas_las_sesiones
- def start_node_service():
+         # Restaurar sesiones (Inbox)
-     global node_qr_process
+         sesiones_restauradas = cargar_todas_las_sesiones()
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+         for wa_id, s in sesiones_restauradas.items():
-     if os.path.exists(qr_dir):
+             sesiones[wa_id] = s
-         try:
+         print(f"[OK] Se restauraron {len(sesiones_restauradas)} conversaciones en memoria desde Firebase.")
-             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
+         
-             node_exe = 'node'
+         # Stickers are now loaded on-demand via Serverless Endpoints.
-             # --- Auto-descubridor/Instalador de Node.js portable ---
+         
-             import platform
+         # Restaurar Etiquetas
-             if platform.system() == 'Linux':
+         from firebase_client import cargar_etiquetas_bd, cargar_grupos_bd
-                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
+         global global_labels, global_groups
-                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
+         global_labels = cargar_etiquetas_bd()
-                 if not os.path.exists(node_portable_exe):
+         print(f"[OK] Se restauraron {len(global_labels)} etiquetas globales.")
-                     try:
+         global_groups = cargar_grupos_bd()
-                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
+         print(f"[OK] Se restauraron {len(global_groups)} grupos virtuales.")
-                     except (FileNotFoun
… [diff truncated]
- **[decision] Optimized Client — prevents null/undefined runtime crashes**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- import subprocess
+ import subprocess
- import os
+ import os
- node_qr_process = None
+ node_qr_process = None
- 
+ 
- @app.on_event('startup')
+ @app.on_event('startup')
- def start_node_service():
+ def start_node_service():
-     global node_qr_process
+     global node_qr_process
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-     if os.path.exists(qr_dir):
+     if os.path.exists(qr_dir):
-         try:
+         try:
-             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
+             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
-             node_exe = 'node'
+             node_exe = 'node'
-             # --- Auto-descubridor/Instalador de Node.js portable ---
+             # --- Auto-descubridor/Instalador de Node.js portable ---
-             import platform
+             import platform
-             if platform.system() == 'Linux':
+             if platform.system() == 'Linux':
-                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
+                 node_bin_dir = os.path.join(os.path.dirname(__file__), 'node_portable')
-                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
+                 node_portable_exe = os.path.join(node_bin_dir, 'node-v20.12.2-linux-x64', 'bin', 'node')
-                 if not os.path.exists(node_portable_exe):
+                 if not os.path.exists(node_portable_exe):
-                     try:
+                     try:
-                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
+                         subprocess.run(['node', '-v'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
-       
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **[convention] Patched security issue Client — protects against XSS and CSRF token theft — confirmed 3x**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- import subprocess
+ import subprocess
- import os
+ import os
- node_qr_process = None
+ node_qr_process = None
- 
+ 
- @app.on_event('startup')
+ @app.on_event('startup')
- def start_node_service():
+ def start_node_service():
-     global node_qr_process
+     global node_qr_process
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-     if os.path.exists(qr_dir):
+     if os.path.exists(qr_dir):
-         try:
+         try:
-             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
+             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
-             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=open('static/node_log.txt', 'w'), stderr=open('static/node_err.txt', 'w'))
+             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=open('static/node_log.txt', 'w'), stderr=open('static/node_err.txt', 'w'))
-         except Exception as e:
+         except Exception as e:
-             print('? Error al iniciar Node:', e)
+             print('? Error al iniciar Node:', e)
- 
+             with open('static/node_status.txt', 'w') as f:
- @app.on_event('shutdown')
+                 f.write(f'PYTHON EXCEPTION:\\n{e}')
- def stop_node_service():
+ 
-     global node_qr_process
+ @app.on_event('shutdown')
-     if node_qr_process:
+ def stop_node_service():
-         try: node_qr_process.terminate()
+     global node_qr_process
-         except: pass
+     if node_qr_process:
- 
+         try: node_qr_process.terminate()
- @app.on_event("startup")
+         except: pass
- def startup_event():
+ 
-     # ── Restaurar toda la memoria y stickers desde Firebase ──
+ @app.on_event("startup")
-     try:
+ def startup_event():
-       
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, node_qr_process]
- **[convention] Optimized Client — prevents null/undefined runtime crashes — confirmed 4x**: - gemini_client = genai.Client(api_key=GEMINI_API_KEY)
+ gemini_client = genai.Client(api_key=GEMINI_API_KEY)
- 
+ 
- import subprocess
+ import subprocess
- import os
+ import os
- node_qr_process = None
+ node_qr_process = None
- 
+ 
- @app.on_event('startup')
+ @app.on_event('startup')
- def start_node_service():
+ def start_node_service():
-     global node_qr_process
+     global node_qr_process
-     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
+     qr_dir = os.path.join(os.path.dirname(__file__), 'qr_service')
-     if os.path.exists(qr_dir):
+     if os.path.exists(qr_dir):
-         try:
+         try:
-             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
+             print('?? [FastAPI] Iniciando microservicio QR Baileys (Node.js)...')
-             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=open('static/node_log.txt', 'w'), stderr=open('static/node_err.txt', 'w'))
+             node_qr_process = subprocess.Popen(['node', 'index.js'], cwd=qr_dir, stdout=open('static/node_log.txt', 'w'), stderr=open('static/node_err.txt', 'w'))
-         except Exception as e:
+         except Exception as e:
-             print('? Error al iniciar Node:', e)
+             print('? Error al iniciar Node:', e)
- 
+ 
- @app.on_event('shutdown')
+ @app.on_event('shutdown')
- def stop_node_service():
+ def stop_node_service():
-     global node_qr_process
+     global node_qr_process
-     if node_qr_process:
+     if node_qr_process:
-         try: node_qr_process.terminate()
+         try: node_qr_process.terminate()
-         req = urllib.request.Request("http://localhost:3000/api/qr/link", headers={'User-Agent': 'Mozilla/5.0'})
+         req = urllib.request.Request("http://127.0.0.1:3000/api/qr/link", headers={'User-Agent': 'Mozilla/5.0'})
- 
+ 
+ 
- **[convention] problem-fix in server.py — confirmed 4x**: - # ------------------------------------------------------------
+ # ------------------------------------------------------------

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] Added JWT tokens authentication — confirmed 4x**: - async def enviar_reaccion_async(numero_destino: str, message_id: str, emoji: str) -> bool:
+ async def enviar_reaccion_async(numero_destino: str, message_id: str, emoji: str, line_id: str = "principal") -> bool:
-     headers = {
+     line_id = _get_line_id(numero_destino, line_id)
-         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
+     if line_id.startswith("qr_"):
-         "Content-Type": "application/json",
+         # TODO: Implementar en Node.js, por ahora silent ignore para no romper UX
-     }
+         return True
-     payload = {
+     headers = {
-         "messaging_product": "whatsapp",
+         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
-         "recipient_type": "individual",
+         "Content-Type": "application/json",
-         "to": numero_destino,
+     }
-         "type": "reaction",
+     payload = {
-         "reaction": {
+         "messaging_product": "whatsapp",
-             "message_id": message_id,
+         "recipient_type": "individual",
-             "emoji": emoji
+         "to": numero_destino,
-         }
+         "type": "reaction",
-     }
+         "reaction": {
-     try:
+             "message_id": message_id,
-         async with httpx.AsyncClient() as client:
+             "emoji": emoji
-             res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
+         }
-             res.raise_for_status()
+     }
-             return True
+     try:
-     except httpx.HTTPStatusError as e:
+         async with httpx.AsyncClient() as client:
-         print(f"[ERROR] Error Meta Reaccion ({e.response.status_code}): {e.response.text}")
+             res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
-         return False
+             res.raise_for_status()
-     except Exception as e:
+             return True
-         print(f"[ERROR] Error enviando reacción: {e}")
+     except httpx.HTTPStatusError as e
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [_get_line_id, META_API_URL, enviar_mensaje, enviar_media, enviar_mensaje_texto]
- **[convention] what-changed in settings.html — confirmed 4x**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
