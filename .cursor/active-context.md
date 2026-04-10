> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Ignorar — protects against XSS and CSRF token theft**: -                                 try:
+                                 import time
-                                     from firebase_client import guardar_sesion_chat
+                                 ts_now = int(time.time())
-                                     guardar_sesion_chat(num_wa, se)
+                                 if status_val == "delivered" and not it.get("delivered_ts"):
-                                 except: pass
+                                     it["delivered_ts"] = ts_now
-                             break
+                                 elif status_val == "read" and not it.get("read_ts"):
-             return {"status": "ok"}
+                                     it["read_ts"] = ts_now
- 
+                                 try:
-         # Si no hay mensajes, ignorar
+                                     from firebase_client import guardar_sesion_chat
-         if "messages" not in changes:
+                                     guardar_sesion_chat(num_wa, se)
-             return {"status": "ok"}
+                                 except: pass
- 
+                             break
-         mensaje_data  = changes["messages"][0]
+             return {"status": "ok"}
-         mensaje_id    = mensaje_data.get("id", "")
+ 
-         mensaje_ts    = mensaje_data.get("timestamp", "")
+         # Si no hay mensajes, ignorar
-         
+         if "messages" not in changes:
-         # Ignorar mensajes duplicados enviados repetidamente por el webhook de Meta
+             return {"status": "ok"}
-         if mensaje_id in mensajes_procesados_ids:
+ 
-             return {"status": "ok"}
+         mensaje_data  = changes["messages"][0]
-         mensajes_procesados_ids[mensaje_id] = True
+         mensaje_id    = mensaje_data.get("id", "")
-         
+         mensaje_ts    = mensaje_data.get("timestamp", "")
-         # Mantener solo los últimos 1000 IDs para evitar fugas sin vaciar el historial r
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **⚠️ GOTCHA: Updated whatsapp_client database schema**: - class EnviarPlantillaPayload(BaseModel):
+ 
-     wa_id: str
+ class EnviarPlantillaPayload(BaseModel):
-     template_name: str
+     wa_id: str
-     language_code: str = "es"
+     template_name: str
- 
+     language_code: str = "es"
- @app.post("/api/admin/enviar_plantilla")
+     body_params: list[str] = None
- async def api_enviar_plantilla(payload: EnviarPlantillaPayload, request: Request):
+ 
-     if not verificar_sesion(request):
+ 
-         raise HTTPException(status_code=403, detail="No autorizado")
+ @app.post("/api/admin/enviar_plantilla")
-         
+ async def api_enviar_plantilla(payload: EnviarPlantillaPayload, request: Request):
-     from whatsapp_client import enviar_plantilla
+     if not verificar_sesion(request):
-     wamid = await enviar_plantilla(payload.wa_id, payload.template_name, payload.language_code)
+         raise HTTPException(status_code=403, detail="No autorizado")
-     
+         
-     if wamid:
+     
-         # Registrar el envío en el historial del dashboard
+     from whatsapp_client import enviar_plantilla
-         from firebase_client import cargar_sesion_chat, guardar_sesion_chat
+     wamid = await enviar_plantilla(payload.wa_id, payload.template_name, payload.language_code, payload.body_params)
-         s = cargar_sesion_chat(payload.wa_id)
+ 
-         if s:
+     
-             if "historial" not in s: s["historial"] = []
+     if wamid:
-             s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
+         # Registrar el envío en el historial del dashboard
-             from datetime import datetime
+         from firebase_client import cargar_sesion_chat, guardar_sesion_chat
-             s["ultima_actividad"] = datetime.utcnow()
+         s = cargar_sesion_chat(payload.wa_id)
-             guardar_sesion_chat(payload.wa_id, s)
+         if s:
-         return {"ok": True, "wamid": wamid
… [diff truncated]

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in POST — reduces excessive function call frequency**: -         window.enviarMensajeDirecto = async function(wa_id, msj) {
+         window._nextQuickReplyTitle = null;
-             if (!msj) return {ok: false};
+ 
-             const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
+         window.enviarMensajeDirecto = async function(wa_id, msj, qrTitle = null) {
-             try {
+             if (!msj) return {ok: false};
-                 const res = await fetch('/api/admin/enviar_manual', {
+             const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
-                     method: 'POST',
+             try {
-                     headers: { 'Content-Type': 'application/json' },
+                 const res = await fetch('/api/admin/enviar_manual', {
-                     body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
+                     method: 'POST',
-                 });
+                     headers: { 'Content-Type': 'application/json' },
- 
+                     body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid, quick_reply_title: qrTitle || window._nextQuickReplyTitle || null })
-                 const data = await res.json();
+                 });
-                 if(!data.ok) { console.error("Error direct send json", data); }
+ 
-                 return data;
+                 const data = await res.json();
-             } catch(e) {
+                 if(!data.ok) { console.error("Error direct send json", data); }
-                 console.error("Error direct send", e);
+                 return data;
-                 return {ok: false, error: e.message || "Red Error"};
+             } catch(e) {
-             }
+                 console.error("Error direct send", e);
-         };
+                 return {ok: false, error: e.message || "Red Error"};
- 
+             }
- 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] Updated schema Handle**: -             // Get text without meta (timestamp/ticks)
+             const qrTitle = bubble.dataset.quickReply || '';
-             const clone = bubble.cloneNode(true);
+             // Get text without meta (timestamp/ticks)
-             const metaEl = clone.querySelector('.msg-meta');
+             const clone = bubble.cloneNode(true);
-             if (metaEl) metaEl.remove();
+             const metaEl = clone.querySelector('.msg-meta');
-             const preview = clone.innerText.trim().slice(0, 200);
+             if (metaEl) metaEl.remove();
- 
+             const preview = clone.innerText.trim().slice(0, 200);
-             document.getElementById('info-preview-text').textContent = preview || '—';
+ 
-             document.getElementById('info-sent-by').textContent = sentBy;
+             document.getElementById('info-preview-text').textContent = preview || '—';
-             document.getElementById('info-sent-ts').textContent = formatTsUnix(ts);
+             document.getElementById('info-sent-by').textContent = sentBy;
-             document.getElementById('info-delivered-ts').textContent = deliveredTs ? formatTsUnix(deliveredTs) : '—';
+             
-             document.getElementById('info-read-ts').textContent = readTs ? formatTsUnix(readTs) : '—';
+             // Handle QR title display
- 
+             const qrRow = document.getElementById('info-row-qr');
-             document.getElementById('msg-info-panel').classList.add('open');
+             if (qrTitle) {
-         }
+                 document.getElementById('info-qr-title').textContent = qrTitle;
- 
+                 qrRow.style.display = 'flex';
-         function closeMsgInfoPanel() {
+             } else {
-             document.getElementById('msg-info-panel').classList.remove('open');
+                 qrRow.style.display = 'none';
-         }
+             }
- 
+             document.getElementById('info-sent-ts').textContent = formatTsUnix(t
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Logout — reduces excessive function call frequency — confirmed 5x**: -         <!-- Logout Icon -->
+         
-         <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-top: auto; color: #ef4444;">
+ 
-             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
+ 
-                 <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
+         
-                 <polyline points="16 17 21 12 16 7"></polyline>
+         <!-- Logout Button (reemplazando al dot) -->
-                 <line x1="21" y1="12" x2="9" y2="12"></line>
+         <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-top: auto; margin-bottom: 20px; color: #ef4444; display: flex; justify-content: center; text-decoration: none;">
-             </svg>
+             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 28px; height: 28px; opacity: 0.8; transition: opacity 0.2s;">
-         </a>
+                 <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
- 
+                 <polyline points="16 17 21 12 16 7"></polyline>
- 
+                 <line x1="21" y1="12" x2="9" y2="12"></line>
-         <!-- Indicador global abajo -->
+             </svg>
-         <div class="bot-status-indicator" title="Estado Global del Bot"></div>
+         </a>
-     </nav>
+ 
- 
+     </nav>
-     <!-- 2. PANEL CENTRAL (Lista de Chats) -->
+ 
-     <div class="chat-list-panel">
+     <!-- 2. PANEL CENTRAL (Lista de Chats) -->
-         <div class="list-header">
+     <div class="chat-list-panel">
-             <h2>Bandeja de Entrada</h2>
+         <div class="list-header">
-             <div class="list-tabs">
+             <h2>Bandeja de Entrada</h2>
-                 <a href="/inbox?tab=all" class="tab {tab_all_active}">Todos</a>
+             <div class="list-tabs">
-                 <a href="/inbox?tab=human" class="tab {tab_
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Click — parallelizes async operations for speed**: -                 extra_data = f' data-sent-by="{sent_by_val}" data-ts="{ts_unix}" data-delivered-ts="{delivered_ts}" data-read-ts="{read_ts}" data-status="{msg_status}"'
+                 qr_title_val = m.get("quick_reply_title", "")
-             
+                 extra_data = f' data-sent-by="{sent_by_val}" data-ts="{ts_unix}" data-delivered-ts="{delivered_ts}" data-read-ts="{read_ts}" data-status="{msg_status}" data-quick-reply="{qr_title_val}"'
-             burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr}{extra_data} title="Click derecho (PC) o mantener presionado (M\u00f3vil) para opciones">{texto_renderizado}{meta_html}</div>'
+             
- 
+             burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr}{extra_data} title="Click derecho (PC) o mantener presionado (M\u00f3vil) para opciones">{texto_renderizado}{meta_html}</div>'
-             
+ 
-         if not burbujas:
+             
-             burbujas = '<div style="text-align:center;opacity:0.5;margin-top:2rem">Conversación iniciada...</div>'
+         if not burbujas:
- 
+             burbujas = '<div style="text-align:center;opacity:0.5;margin-top:2rem">Conversación iniciada...</div>'
-         # Cabecera superior del chat
+ 
-         status_bar = ""
+         # Cabecera superior del chat
-         if not activo_chat:
+         status_bar = ""
-             status_bar = f"""
+         if not activo_chat:
-             <div style="background:var(--danger-color);color:white;padding:0.5rem 1rem;font-size:0.85rem;font-weight:600;display:flex;justify-content:space-between;align-items:center;">
+             status_bar = f"""
-                 Atención manual en curso
+             <div style="background:var(--danger-color);color:white;padding:0.5rem 1rem;font-size:0.85rem;font-weight:600;display:flex;justify-content:space-between;align-items:center;">
-                 <form method="post" action="/admin/reactivar/{wa_id}" style="margin:0">
+     
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[decision] Optimized Consultas**: - # ============================================================
+ # ============================================================
- #  firebase_client.py — Consultas a Firestore con Admin SDK
+ #  firebase_client.py — Consultas a Firestore con Admin SDK
- # ============================================================
+ # ============================================================
- import os
+ import os
- import firebase_admin
+ import firebase_admin
- from firebase_admin import credentials, firestore
+ from firebase_admin import credentials, firestore
- from google.cloud.firestore_v1.base_query import FieldFilter
+ from google.cloud.firestore_v1.base_query import FieldFilter
- 
+ 
- from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_JSON, COLECCION_PEDIDOS
+ from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_JSON, COLECCION_PEDIDOS
- 
+ 
- 
+ 
- def inicializar_firebase():
+ def inicializar_firebase():
-     """Inicializa Firebase Admin una sola vez."""
+     """Inicializa Firebase Admin una sola vez."""
-     if not firebase_admin._apps:
+     if not firebase_admin._apps:
-         if FIREBASE_JSON:
+         if FIREBASE_JSON:
-             import json
+             import json
-             try:
+             try:
-                 cred_dict = json.loads(FIREBASE_JSON)
+                 cred_dict = json.loads(FIREBASE_JSON)
-                 cred = credentials.Certificate(cred_dict)
+                 cred = credentials.Certificate(cred_dict)
-             except Exception as e:
+             except Exception as e:
-                 raise ValueError(f"❌ Error parseando FIREBASE_JSON: {e}")
+                 raise ValueError(f"❌ Error parseando FIREBASE_JSON: {e}")
-         else:
+         else:
-             if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
+             if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
-                 raise FileNotFoundError(
+                 raise FileNotFoundError(
-                     f"\n
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id, guardar_sesion_chat]
- **[what-changed] Updated schema USER**: - 
+ 
- def guardar_grupo_bd(grupo: dict):
+ def guardar_grupo_bd(grupo: dict):
-     db = inicializar_firebase()
+     db = inicializar_firebase()
-     if db: db.collection("virtual_groups").document(grupo["id"]).set(grupo)
+     if db: db.collection("virtual_groups").document(grupo["id"]).set(grupo)
- 
+ 
- def eliminar_grupo_bd(grupo_id: str):
+ def eliminar_grupo_bd(grupo_id: str):
-     db = inicializar_firebase()
+     db = inicializar_firebase()
-     if db: db.collection("virtual_groups").document(grupo_id).delete()
+     if db: db.collection("virtual_groups").document(grupo_id).delete()
- 
+ 
- def cargar_grupos_bd() -> list:
+ def cargar_grupos_bd() -> list:
-     db = inicializar_firebase()
+     db = inicializar_firebase()
-     if not db: return []
+     if not db: return []
-     docs = db.collection("virtual_groups").stream()
+     docs = db.collection("virtual_groups").stream()
-     return [d.to_dict() for d in docs]
+     return [d.to_dict() for d in docs]
- 
+ 
- 
+ 
- # ─────────────────────────────────────────────
+ # ─────────────────────────────────────────────
- #  USER AUTENTICATION AND MANAGEMENT
+ #  USER AUTENTICATION AND MANAGEMENT
- # ─────────────────────────────────────────────
+ # ─────────────────────────────────────────────
- 
+ 
- def crear_usuario(username: str, password_hash: str) -> bool:
+ def crear_usuario(username: str, password_hash: str) -> bool:
-     db = inicializar_firebase()
+     db = inicializar_firebase()
-     doc_ref = db.collection("usuarios_atc").document(username)
+     doc_ref = db.collection("usuarios_atc").document(username)
-     if doc_ref.get().exists:
+     if doc_ref.get().exists:
-         return False
+         return False
-     doc_ref.set({
+     doc_ref.set({
-         "password": password_hash,
+         "password": password_hash,
-         "estado": "pendiente",
+         "estado": "pendiente",
-         "permisos": []
+         "permisos": []
-     })
+     })
- 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id, guardar_sesion_chat]
- **[what-changed] Updated configuration Obtener**: -         # Obtener usuario que envió el mensaje
+         # Obtener usuario que envió el mensaje — usar nombre visible si está configurado
-         sent_by_name = usuario_sesion.get("username", "Agente") if usuario_sesion else "Agente"
+         sent_by_name = (usuario_sesion.get("nombre") or usuario_sesion.get("username", "Agente")) if usuario_sesion else "Agente"

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[convention] Fixed null crash in Nombre — parallelizes async operations for speed — confirmed 4x**: -                     <th>Estado</th>
+                     <th>Nombre Visible</th>
-                     <th>Permisos</th>
+                     <th>Estado</th>
-                     <th>Acciones</th>
+                     <th>Permisos</th>
-                 </tr>
+                     <th>Acciones</th>
-             </thead>
+                 </tr>
-             <tbody id="users-body">
+             </thead>
-                 <tr><td colspan="4" style="text-align:center">Cargando...</td></tr>
+             <tbody id="users-body">
-             </tbody>
+                 <tr><td colspan="4" style="text-align:center">Cargando...</td></tr>
-         </table>
+             </tbody>
- 
+         </table>
-         <script>
+ 
-             async function loadUsers() {
+         <script>
-                 const res = await fetch('/api/usuarios/list');
+             async function loadUsers() {
-                 const users = await res.json();
+                 const res = await fetch('/api/usuarios/list');
-                 const tbody = document.getElementById('users-body');
+                 const users = await res.json();
-                 tbody.innerHTML = '';
+                 const tbody = document.getElementById('users-body');
-                 
+                 tbody.innerHTML = '';
-                 users.forEach(u => {
+                 
-                     const isAdmin = u.permisos.includes('admin');
+                 users.forEach(u => {
-                     tbody.innerHTML += `<tr>
+                     const isAdmin = u.permisos.includes('admin');
-                             <td>${u.username}</td>
+                     tbody.innerHTML += `<tr>
-                             <td><span class="badge ${u.estado}">${u.estado}</span></td>
+                             <td>${u.username}</td>
-                             <td>${isAdmin ? 'Admin' : 'Estándar'}</td>
+                             <td><input type="tex
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[convention] Replaced auth server — confirmed 3x**: -         save_sessions()
+     delete_session_from_firebase(token)

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[what-changed] Replaced dependency Plantilla**: -             s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
+         s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
-             from datetime import datetime
+         from datetime import datetime
-             s["ultima_actividad"] = datetime.utcnow()
+         s["ultima_actividad"] = datetime.utcnow()
-             guardar_sesion_chat(payload.wa_id, s)
+         guardar_sesion_chat(payload.wa_id, s)

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[what-changed] Added session cookies authentication**: -         if s:
+         if not s:
-             if "historial" not in s: s["historial"] = []
+             # Create a brand new session if it doesn't exist so it appears in Inbox immediately
-             s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
+             s = {
-             from datetime import datetime
+                 "historial": [], 
-             s["ultima_actividad"] = datetime.utcnow()
+                 "estado_bot": "activo",
-             guardar_sesion_chat(payload.wa_id, s)
+                 "etiquetas": [],
-         return {"ok": True, "wamid": wamid}
+                 "ultimo_mensaje": "",
-     return {"ok": False, "error": "No se pudo enviar (Verifica que el WABA ID sea el correcto o Meta la rechazó)."}
+                 "clienteNombre": "Desconocido (Plantilla saliente)"
- 
+             }
- 
+         
- # ============================================================
+         if "historial" not in s: s["historial"] = []
- #  API DE GESTOR DE ETIQUETAS Y ASIGNACIONES
+ 
- # ============================================================
+             s["historial"].append({"role": "assistant", "content": f"[Plantilla enviada: {payload.template_name}]", "msg_id": wamid})
- 
+             from datetime import datetime
- from typing import Optional
+             s["ultima_actividad"] = datetime.utcnow()
- 
+             guardar_sesion_chat(payload.wa_id, s)
- class InitChatPayload(BaseModel):
+         return {"ok": True, "wamid": wamid}
-     wa_id: str
+     return {"ok": False, "error": "No se pudo enviar (Verifica que el WABA ID sea el correcto o Meta la rechazó)."}
- @app.post("/api/admin/chat/init")
+ 
- async def api_init_chat(payload: InitChatPayload, request: Request):
+ # ============================================================
-     if not verificar_sesion(request): raise HTTPException(status_code=403)
+ #  API D
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[problem-fix] problem-fix in whatsapp_client.py**: -     }
+     try:
-     try:
+         async with httpx.AsyncClient() as client:
-         async with httpx.AsyncClient() as client:
+             res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
-             res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
+             res.raise_for_status()
-             res.raise_for_status()
+             data = res.json()
-             data = res.json()
+             return data.get("messages", [{}])[0].get("id")
-             return data.get("messages", [{}])[0].get("id")
+     except httpx.HTTPStatusError as e:
-     except httpx.HTTPStatusError as e:
+         print(f"❌ Error Meta Plantilla ({e.response.status_code}): {e.response.text}")
-         print(f"❌ Error Meta Plantilla ({e.response.status_code}): {e.response.text}")
+         return None
-         return None
+     except Exception as e:
-     except Exception as e:
+         print(f"❌ Error enviando plantilla: {e}")
-         print(f"❌ Error enviando plantilla: {e}")
+         return None
-         return None
+ 
- 

📌 IDE AST Context: Modified symbols likely include [META_API_URL, enviar_mensaje, enviar_media, enviar_mensaje_texto, obtener_media_url]
- **[convention] Added JWT tokens authentication — confirmed 4x**: - async def enviar_plantilla(numero_destino: str, template_name: str, language_code: str = "es") -> str | None:
+ 
-     """Envía un Message Template preaprobado por Meta."""
+ async def enviar_plantilla(numero_destino: str, template_name: str, language_code: str = "es", body_params: list[str] = None) -> str | None:
-     headers = {
+     """Envía un Message Template preaprobado por Meta."""
-         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
+     headers = {
-         "Content-Type": "application/json",
+         "Authorization": f"Bearer {META_ACCESS_TOKEN}",
-     }
+         "Content-Type": "application/json",
-     payload = {
+     }
-         "messaging_product": "whatsapp",
+     
-         "recipient_type": "individual",
+     template_data = {
-         "to": numero_destino,
+         "name": template_name,
-         "type": "template",
+         "language": {
-         "template": {
+             "code": language_code
-             "name": template_name,
+         }
-             "language": {
+     }
-                 "code": language_code
+     
-             }
+     if body_params:
-         }
+         template_data["components"] = [
-     }
+             {
-     try:
+                 "type": "body",
-         async with httpx.AsyncClient() as client:
+                 "parameters": [
-             res = await client.post(META_API_URL, headers=headers, json=payload, timeout=10)
+                     {"type": "text", "text": str(p)} for p in body_params
-             res.raise_for_status()
+                 ]
-             data = res.json()
+             }
-             return data.get("messages", [{}])[0].get("id")
+         ]
-     except httpx.HTTPStatusError as e:
+ 
-         print(f"❌ Error Meta Plantilla ({e.response.status_code}): {e.response.text}")
+     payload = {
-         return None
+         "messaging_product": "whatsapp",
-     except Exception as e:
+         "recipient_
… [diff truncated]
