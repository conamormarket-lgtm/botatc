> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Exception — protects against XSS and CSRF token theft**: -     except Exception as e:
+         return response.text.strip()
-         import traceback
+     except Exception as e:
-         with open("error_gemini.txt", "w") as f:
+         import traceback
-             f.write(traceback.format_exc())
+         with open("error_gemini.txt", "w") as f:
-         print(f"❌ Error Gemini: {e}")
+             f.write(traceback.format_exc())
-         return ""
+         print(f"❌ Error Gemini: {e}")
- 
+         return ""
- def recortar_historial(historial: list[dict]) -> list[dict]:
+ 
-     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
+ def recortar_historial(historial: list[dict]) -> list[dict]:
-     system = [historial[0]]
+     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
-     turnos = historial[1:]
+     system = [historial[0]]
-     
+     turnos = historial[1:]
-     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
+     
-     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
+     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
-         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
+     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
-         
+         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
-         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
+         
-         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
+         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
-         if turnos and turnos[0]["role"] == "assistant":
+         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
-             turnos = turnos[1:]
+         if turnos and turnos[0]["role"] == "assistant":
-             
+             turnos = turnos[1:]
-     return system + turnos
+             
- 
+     return system + turn
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **⚠️ GOTCHA: Replaced auth Conserva**: -     except Exception as e:
+         return ""
-         import traceback
+ 
-         with open("error_gemini.txt", "w") as f:
+ 
-             f.write(traceback.format_exc())
+ def recortar_historial(historial: list[dict]) -> list[dict]:
-         print(f"❌ Error Gemini: {e}")
+     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
-         return "Disculpa, tuve un problema técnico. Intenta en un momento. 🙏"
+     system = [historial[0]]
- 
+     turnos = historial[1:]
- 
+     
- def recortar_historial(historial: list[dict]) -> list[dict]:
+     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
-     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
+     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
-     system = [historial[0]]
+         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
-     turnos = historial[1:]
+         
-     
+         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
-     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
+         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
-     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
+         if turnos and turnos[0]["role"] == "assistant":
-         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
+             turnos = turnos[1:]
-         
+             
-         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
+     return system + turnos
-         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
+ 
-         if turnos and turnos[0]["role"] == "assistant":
+ 
-             turnos = turnos[1:]
+ # ─────────────────────────────────────────────
-             
+ #  Lógica de escalación
-     return system + turnos
+ # ─────────────────────────────────────────────
- 
+ def procesar_escalacion(nu
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
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

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in Cargar — wraps unsafe operation in error boundary**: -                     alert("✅ Plantilla enviada. La ventana de 24 horas se debería abrir si el cliente responde.");
+                     // Cargar el chat inmediatamente para ver la burbuja
-                 } else {
+                     window.location.reload();
-                     alert("❌ Error: " + data.error);
+                 } else {
-                 }
+                     alert("❌ Error: " + data.error);
-             } catch (e) {
+                 }
-                 alert("Falla de conectividad");
+             } catch (e) {
-             }
+                 alert("Falla de conectividad");
-         }
+             }
- 
+         }
-         // ================= ETIQUETAS (LABELS) LOGIC =================
+ 
-         function crearGlobalLabel() {
+         // ================= ETIQUETAS (LABELS) LOGIC =================
-             // Abrir el modal en lugar de prompt()
+         function crearGlobalLabel() {
-             const modal = document.getElementById("createLabelModal");
+             // Abrir el modal en lugar de prompt()
-             if (modal) {
+             const modal = document.getElementById("createLabelModal");
-                 document.getElementById("newLabelName").value = "";
+             if (modal) {
-                 // Reset a color por defecto
+                 document.getElementById("newLabelName").value = "";
-                 const firstColor = document.getElementById("color-grid-container").querySelector('.color-option');
+                 // Reset a color por defecto
-                 if (firstColor) seleccionarColorEtiqueta("#3b82f6", firstColor);
+                 const firstColor = document.getElementById("color-grid-container").querySelector('.color-option');
-                 modal.style.display = "flex";
+                 if (firstColor) seleccionarColorEtiqueta("#3b82f6", firstColor);
-             }
+                 modal.style.display = "flex";
-         }
+    
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in POST — wraps unsafe operation in error boundary**: -             document.getElementById("templateMenu").style.display = "none";
+             const tMenu = document.getElementById("templateMenu");
- 
+             if(tMenu) tMenu.style.display = "none";
-             try {
+ 
-                 const res = await fetch("/api/admin/enviar_plantilla", {
+             try {
-                     method: "POST",
+                 const res = await fetch("/api/admin/enviar_plantilla", {
-                     headers: { "Content-Type": "application/json" },
+                     method: "POST",
-                     body: JSON.stringify({ wa_id: wa_id, template_name: name, language_code: lang })
+                     headers: { "Content-Type": "application/json" },
-                 });
+                     body: JSON.stringify({ wa_id: wa_id, template_name: name, language_code: lang })
-                 const data = await res.json();
+                 });
-                 if (data.ok) {
+                 const data = await res.json();
-                     alert("✅ Plantilla enviada. La ventana de 24 horas se debería abrir si el cliente responde.");
+                 if (data.ok) {
-                 } else {
+                     alert("✅ Plantilla enviada. La ventana de 24 horas se debería abrir si el cliente responde.");
-                     alert("❌ Error: " + data.error);
+                 } else {
-                 }
+                     alert("❌ Error: " + data.error);
-             } catch (e) {
+                 }
-                 alert("Falla de conectividad");
+             } catch (e) {
-             }
+                 alert("Falla de conectividad");
-         }
+             }
- 
+         }
-         // ================= ETIQUETAS (LABELS) LOGIC =================
+ 
-         function crearGlobalLabel() {
+         // ================= ETIQUETAS (LABELS) LOGIC =================
-             // Abrir el modal en lugar de prompt()
+         function crearGlobalL
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
- **[problem-fix] Fixed null crash in Formatear — parallelizes async operations for speed**: -             wamid = m.get("msg_id", "")
+             # Formatear la vista de plantillas salientes
-             wamid_attr = f' data-wamid="{wamid}"' if wamid else ""
+             match_tpl = re.match(r"^\[Plantilla enviada:\s*(.*?)\]$", texto_renderizado)
-             
+             if match_tpl:
-             meta_html = ""
+                 tpl_name = match_tpl.group(1)
-             ts_html = ""
+                 texto_renderizado = f'<div style="background:rgba(255,255,255,0.05); border-left:3px solid #10b981; padding:0.6rem; border-radius:6px; margin:-0.2rem;"><div style="font-size:0.7rem; color:#10b981; font-weight:600; text-transform:uppercase; margin-bottom:0.3rem; display:flex; align-items:center; gap:0.3rem;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> PLANTILLA META</div><div style="font-size:0.95rem; font-weight:500;">{tpl_name}</div></div>'
-             status_html = ""
+                 
- 
+             wamid = m.get("msg_id", "")
-             if "timestamp" in m:
+             wamid_attr = f' data-wamid="{wamid}"' if wamid else ""
-                 try:
+             
-                     ts_val = int(m["timestamp"])
+             meta_html = ""
-                     if ts_val > 1e11: ts_val //= 1000
+             ts_html = ""
-                     utc_dt = datetime.utcfromtimestamp(ts_val)
+             status_html = ""
-                     lima_dt = utc_dt - timedelta(hours=5)
+ 
-                     ts_str = lima_dt.strftime("%H:%M")
+             if "timestamp" in m:
-                     ts_html = f'<span class="msg-ts">{ts_str}</span>'
+                 try:
-                 except:
+          
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]
- **[convention] Fixed null crash in Exception — protects against XSS and CSRF token theft — confirmed 3x**: -         return response.text.strip()
+     except Exception as e:
-         return ""
+         import traceback
- 
+         with open("error_gemini.txt", "w") as f:
- 
+             f.write(traceback.format_exc())
- def recortar_historial(historial: list[dict]) -> list[dict]:
+         print(f"❌ Error Gemini: {e}")
-     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
+         return ""
-     system = [historial[0]]
+ 
-     turnos = historial[1:]
+ 
-     
+ def recortar_historial(historial: list[dict]) -> list[dict]:
-     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
+     """Conserva system prompt + últimos N turnos, asegurando que inicie con 'user'."""
-     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
+     system = [historial[0]]
-         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
+     turnos = historial[1:]
-         
+     
-         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
+     # Si excede el límite (ej. 6 = 3 turnos usuario-asistente)
-         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
+     if len(turnos) > MAX_HISTORIAL_TURNOS * 2:
-         if turnos and turnos[0]["role"] == "assistant":
+         turnos = turnos[-(MAX_HISTORIAL_TURNOS * 2):]
-             turnos = turnos[1:]
+         
-             
+         # Gemini (y Groq) requieren que el primer mensaje después del system sea del 'user'.
-     return system + turnos
+         # Si al cortar el array el primer elemento quedó como 'assistant' (model), lo volamos para emparejar.
- 
+         if turnos and turnos[0]["role"] == "assistant":
- 
+             turnos = turnos[1:]
- # ─────────────────────────────────────────────
+             
- #  Lógica de escalación
+     return system + turnos
- # ─────────────────────────────────────────────
+ 
- def procesar_escalacion(numero_wa: str, sesion:
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
