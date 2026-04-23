> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `server.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...**: -     # Inyectar tema del usuario (colores configurados en Mi Perfil)
+     # Inyectar ES_ADMIN para el JS del pipeline
-     html = inyectar_tema_global(request, html)
+     html = html.replace('<style id="custom-theme-css">', f'<script>window.ES_ADMIN = {es_admin_str};</script><style id="custom-theme-css">')
-     return HTMLResponse(html)
+     # Inyectar tema del usuario (colores configurados en Mi Perfil)
- 
+     html = inyectar_tema_global(request, html)
- from typing import List
+     return HTMLResponse(html)
- @app.post("/api/admin/stickers/upload")
+ 
- async def upload_stickers(files: List[UploadFile] = File(...)):
+ from typing import List
-     """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
+ 
-     try:
+ @app.post("/api/admin/stickers/upload")
-         import os
+ async def upload_stickers(files: List[UploadFile] = File(...)):
-         from firebase_client import guardar_sticker_en_bd
+     """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
-         count = 0
+     try:
-         for file in files:
+         import os
-             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
+         from firebase_client import guardar_sticker_en_bd
-                 # Extraemos solo el nombre del archivo, ignorando subcarpetas
+         count = 0
-                 basename = os.path.basename(file.filename)
+         for file in files:
-                 content = await file.read()
+             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
-                 
+                 # Extraemos solo el nombre del archivo, ignorando subcarpetas
-                 # Guardar en Base de Datos (Persistente)
+                 basename = os.path.basename(file.filename)
-                 guardar_sticker_en_bd(basename, content)
+                 content = await file.read()
-                 count += 1
+                 # Guardar
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...**: -     # Inyectar custom theme igual que en inbox
+     # Inyectar tema del usuario (colores configurados en Mi Perfil)
-     try:
+     html = inyectar_tema_global(request, html)
-         from firebase_client import cargar_configuracion_tema
+ 
-         cfg = cargar_configuracion_tema()
+     return HTMLResponse(html)
-         if cfg:
+ 
-             import json as _j2
+ 
-             custom_css = cfg.get("custom_css", "")
+ from typing import List
-             html = html.replace('<style id="custom-theme-css">', f'<script>window.ES_ADMIN = {es_admin_str};</script><style id="custom-theme-css">{custom_css}')
+ 
-     except: pass
+ @app.post("/api/admin/stickers/upload")
- 
+ async def upload_stickers(files: List[UploadFile] = File(...)):
-     return HTMLResponse(html)
+     """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
- 
+     try:
- from typing import List
+         import os
- 
+         from firebase_client import guardar_sticker_en_bd
- @app.post("/api/admin/stickers/upload")
+         count = 0
- async def upload_stickers(files: List[UploadFile] = File(...)):
+         for file in files:
-     """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
+             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
-     try:
+                 # Extraemos solo el nombre del archivo, ignorando subcarpetas
-         import os
+                 basename = os.path.basename(file.filename)
-         from firebase_client import guardar_sticker_en_bd
+                 content = await file.read()
-         count = 0
+                 
-         for file in files:
+                 # Guardar en Base de Datos (Persistente)
-             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
+                 guardar_sticker_en_bd(basename, content)
-                 # Extraemos solo el nombre del archivo, ignorando subcarpetas
+  
… [diff truncated]
- **⚠️ GOTCHA: Patched security issue Tambi — protects against XSS and CSRF token theft**: -         _synced = 0
+         # También busca pedidos para sesiones sin datos_pedido (evita tener que usar el botón Sincronizar)
-         for _wa_id, _s in sesiones.items():
+         _synced = 0
-             if _s.get("lineId", "principal") == "principal" and _s.get("datos_pedido"):
+         _fetched = 0
-                 _eg = _s["datos_pedido"].get("estadoGeneral", "")
+         from firebase_client import buscar_pedido_por_telefono, guardar_sesion_chat
-                 _stage_id = next(
+         for _wa_id, _s in sesiones.items():
-                     (st["id"] for st in global_pipeline_stages
+             if _s.get("lineId", "principal") != "principal":
-                      if _eg in st.get("match_values", [])),
+                 continue
-                     None
+             # Si no tiene pedido vinculado, intentar buscarlo por teléfono
-                 )
+             if not _s.get("datos_pedido"):
-                 if _s.get("pipeline_stage") != _stage_id:
+                 try:
-                     _s["pipeline_stage"] = _stage_id
+                     _pedidos = buscar_pedido_por_telefono(_wa_id)
-                     _synced += 1
+                     if _pedidos:
-         if _synced:
+                         _s["datos_pedido"] = _pedidos[0]
-             print(f"[OK] Pipeline: {_synced} sesiones sincronizadas al arranque.")
+                         _s["pedidos_multiples"] = _pedidos
-     except Exception as e:
+                         _fetched += 1
-         print(f"[ERROR] Error al restaurar datos desde Firebase: {e}")
+                 except Exception as _fe:
- 
+                     pass  # No bloquear el arranque si falla una búsqueda
-     try:
+             # Asignar etapa según estadoGeneral
-         from pedidos_observer import iniciar_observador_pedidos
+             _eg = (_s.get("datos_pedido") or {}).get("estadoGeneral", "")
-         import threading
+             _stage_id = next
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Patched security issue Colitas — parallelizes async operations for speed**: - def renderizar_inbox(request: Request, wa_id: str = None, tab: str = "all", label_filter: str = None, unread: str = None, line_filter: str = "all", stage: str = "all"):
+                   width:100%;margin:0 auto}}
-     import json
+       .mensaje{{display:flex;flex-direction:column;max-width:80%;position:relative}}
-     aliases = {}
+       .bot-lado{{align-self:flex-end}}
-     try:
+       .user-lado{{align-self:flex-start}}
-         with open("line_aliases.json", "r", encoding="utf-8") as f:
+       .remitente{{font-size:.75rem;color:var(--text-gray);margin-bottom:.25rem;font-weight:600}}
-             aliases = json.load(f)
+       .bot-lado .remitente{{text-align:right}}
-     except: pass
+       .burbuja-bot{{background:var(--wa-bot);border-radius:12px 0 12px 12px;padding:.75rem 1rem;
-     
+                    font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
-     import os
+                    color:var(--text-dark);position:relative}}
-     # Si estamos en Vercel (servidor sin estado fraccionado), forzamos lectura de BD para el chat activo actual
+       .burbuja-user{{background:var(--wa-me);border-radius:0 12px 12px 12px;padding:.75rem 1rem;
-     if wa_id and os.environ.get("VERCEL"):
+                     font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
-         try:
+                     color:var(--text-dark);position:relative}}
-             from firebase_client import cargar_sesion_chat
+       /* Colitas de las burbujas */
-             s_db = cargar_sesion_chat(wa_id)
+       .burbuja-bot::before{{content:"";position:absolute;top:0;right:-8px;
-             if s_db:
+                             border-left:8px solid var(--wa-bot);border-bottom:8px solid transparent}}
-                 sesiones[wa_id] = s_db
+       .burbuja-user::before{{content:"";position:absolute;top:0;left:-8px;
-         except Exception:
+                              border-right:8px so
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Fixed null crash in HTMLResponse — evolves the database schema to support new...**: - from typing import List
+ @app.get("/pipeline", response_class=HTMLResponse)
- 
+ async def pipeline_view(request: Request):
- @app.post("/api/admin/stickers/upload")
+     if not verificar_sesion(request):
- async def upload_stickers(files: List[UploadFile] = File(...)):
+         return HTMLResponse(obtener_login_html(), status_code=401)
-     """Recibe múltiples archivos webp/png y los guarda directamente a Firestore."""
+     import os, json as _json
-     try:
+     if not os.path.exists("pipeline.html"):
-         import os
+         return HTMLResponse("<h2 style='font-family:sans-serif;padding:2rem'>pipeline.html no encontrado.</h2>")
-         from firebase_client import guardar_sticker_en_bd
+     with open("pipeline.html", "r", encoding="utf-8") as f:
-         count = 0
+         html = f.read()
-         for file in files:
+ 
-             if file.filename.endswith(".webp") or file.filename.endswith(".png"):
+     global global_pipeline_stages
-                 # Extraemos solo el nombre del archivo, ignorando subcarpetas
+     if not global_pipeline_stages:
-                 basename = os.path.basename(file.filename)
+         try:
-                 content = await file.read()
+             from firebase_client import cargar_pipeline_stages_bd
-                 
+             global_pipeline_stages = cargar_pipeline_stages_bd()
-                 # Guardar en Base de Datos (Persistente)
+         except: pass
-                 guardar_sticker_en_bd(basename, content)
+ 
-                 
+     # Construir columnas del pipeline: chats de línea principal agrupados por etapa
-                 count += 1
+     from datetime import datetime, timezone
-         return {"ok": True, "count": count}
+     ahora = datetime.now(timezone.utc).replace(tzinfo=None)
-     except Exception as e:
+ 
-         return {"ok": False, "error": str(e)}
+     # Sesiones de la línea principal, no archivadas
- 
+     chats_principa
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Updated firebase_client database schema**: - class ChatActionPayload(BaseModel):
+ # ─────────────────────────────────────────────
-     wa_id: str
+ #  PIPELINE API ENDPOINTS
-     action: str
+ # ─────────────────────────────────────────────
- @app.post("/api/admin/chat/action")
+ class PipelineStagePayload(BaseModel):
- async def api_chat_action(payload: ChatActionPayload, request: Request):
+     id: Optional[str] = None
-     if not verificar_sesion(request):
+     name: str
-         raise HTTPException(status_code=403, detail="No autorizado")
+     color: str = "#94a3b8"
-         
+     order: int = 999
-     from firebase_client import cargar_sesion_chat, guardar_sesion_chat, inicializar_firebase, guardar_grupo_bd, eliminar_grupo_bd
+     is_final: bool = False
-     wa_id = payload.wa_id
+     match_values: list = []
-     action = payload.action
+ 
-     global global_groups
+ class PipelineReorderPayload(BaseModel):
-     
+     ids: list
-     if wa_id.startswith("vg_"):
+ 
-         found_g = next((g for g in global_groups if g.get("id") == wa_id), None)
+ @app.get("/api/pipeline/stages")
-         if not found_g and action != "delete": return {"ok": False, "error": "Grupo no existe"}
+ async def api_pipeline_list_stages(request: Request):
-         
+     if not verificar_sesion(request):
-         if action == "archive":
+         raise HTTPException(status_code=403, detail="No autorizado")
-             found_g["is_archived"] = not found_g.get("is_archived", False)
+     global global_pipeline_stages
-             try: guardar_grupo_bd(found_g)
+     if not global_pipeline_stages:
-             except: pass
+         try:
-             return {"ok": True, "state": found_g["is_archived"]}
+             from firebase_client import cargar_pipeline_stages_bd
-         elif action == "pin":
+             global_pipeline_stages = cargar_pipeline_stages_bd()
-             found_g["is_pinned"] = not found_g.get("is_pinned", False)
+         except Excep
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Patched security issue Cargar — protects against XSS and CSRF token theft**: -     except Exception as e:
+ 
-         print(f"[ERROR] Error al restaurar datos desde Firebase: {e}")
+         # Cargar etapas del pipeline
- 
+         from firebase_client import cargar_pipeline_stages_bd
-     try:
+         global global_pipeline_stages
-         from pedidos_observer import iniciar_observador_pedidos
+         global_pipeline_stages = cargar_pipeline_stages_bd()
-         import threading
+         print(f"[OK] Se cargaron {len(global_pipeline_stages)} etapas de pipeline.")
-         t = threading.Thread(target=iniciar_observador_pedidos, daemon=True)
+ 
-         t.start()
+         # Batch sync: asignar pipeline_stage a sesiones de la línea principal
-     except: pass
+         _synced = 0
- 
+         for _wa_id, _s in sesiones.items():
- # Sesiones en memoria: {numero_wa: SesionDict}
+             if _s.get("lineId", "principal") == "principal" and _s.get("datos_pedido"):
- # numero_wa tiene código de país: "51945257117"
+                 _eg = _s["datos_pedido"].get("estadoGeneral", "")
- sesiones: dict[str, dict] = {}
+                 _stage_id = next(
- global_labels: list = []
+                     (st["id"] for st in global_pipeline_stages
- global_groups: list = []
+                      if _eg in st.get("match_values", [])),
- 
+                     None
- # Interruptor global — False = bot completamente apagado
+                 )
- BOT_GLOBAL_ACTIVO: bool = True
+                 if _s.get("pipeline_stage") != _stage_id:
- 
+                     _s["pipeline_stage"] = _stage_id
- # Cola para debouncing (acumular múltiples mensajes rápidos del mismo usuario)
+                     _synced += 1
- mensajes_pendientes: dict[str, list[str]] = {}
+         if _synced:
- import asyncio
+             print(f"[OK] Pipeline: {_synced} sesiones sincronizadas al arranque.")
- user_locks: dict[str, asyncio.Lock] = {}
+     except Exception as e:
- mensajes_procesados_ids = {}
+         print(f
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **⚠️ GOTCHA: Optimized None — ensures atomic multi-step database operations**: -             "lineId": sesion_dict.get("lineId", "principal")
+             "lineId": sesion_dict.get("lineId", "principal"),
-         }
+             "pipeline_stage": sesion_dict.get("pipeline_stage", None),
-         
+         }
-         # Firestore maneja datetimes nativamente
+         
-         doc_ref.set(data_to_save)
+         # Firestore maneja datetimes nativamente
-         print(f"[OK] [FIREBASE-DEBUG] Guardado exitoso: {numero_wa}")
+         doc_ref.set(data_to_save)
-     except Exception as e:
+         print(f"[OK] [FIREBASE-DEBUG] Guardado exitoso: {numero_wa}")
-         import traceback
+     except Exception as e:
-         with open("firebase_debug_error.log", "a", encoding="utf-8") as f:
+         import traceback
-             f.write(f"ERROR GUARDANDO {numero_wa}:\n")
+         with open("firebase_debug_error.log", "a", encoding="utf-8") as f:
-             traceback.print_exc(file=f)
+             f.write(f"ERROR GUARDANDO {numero_wa}:\n")
-             f.write("-" * 50 + "\n")
+             traceback.print_exc(file=f)
-         print(f"[ERROR] [FIREBASE-DEBUG] ERROR CATCHED IN FIREBASE CLIENT: {e}")
+             f.write("-" * 50 + "\n")
-         raise e
+         print(f"[ERROR] [FIREBASE-DEBUG] ERROR CATCHED IN FIREBASE CLIENT: {e}")
- 
+         raise e
- def cargar_sesion_chat(numero_wa: str) -> dict | None:
+ 
-     """Carga y devuelve la sesión si existe en Firestore."""
+ def cargar_sesion_chat(numero_wa: str) -> dict | None:
-     db = inicializar_firebase()
+     """Carga y devuelve la sesión si existe en Firestore."""
-     doc_ref = db.collection("chats_atc").document(numero_wa)
+     db = inicializar_firebase()
-     doc = doc_ref.get()
+     doc_ref = db.collection("chats_atc").document(numero_wa)
-     
+     doc = doc_ref.get()
-     if doc.exists:
+     
-         data = doc.to_dict()
+     if doc.exists:
-         # Aseguramos de que todo lo necesario esté para compatibi
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [inicializar_firebase, _buscar, buscar_pedido_por_telefono, buscar_pedido_por_id, guardar_sesion_chat]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] Updated firebase_client database schema**: -     synced = 0
+     from firebase_client import buscar_pedido_por_telefono, guardar_sesion_chat
-     for wa_id, s in sesiones.items():
+     synced = 0
-         if s.get("lineId", "principal") != "principal":
+     fetched = 0
-             continue
+     for wa_id, s in sesiones.items():
-         eg = (s.get("datos_pedido") or {}).get("estadoGeneral", "")
+         if s.get("lineId", "principal") != "principal":
-         new_stage = next(
+             continue
-             (st["id"] for st in global_pipeline_stages if eg in st.get("match_values", [])),
+         # Si no tiene datos_pedido, intentar buscar el pedido por teléfono
-             None
+         if not s.get("datos_pedido"):
-         )
+             # wa_id suele ser el número de teléfono directo (ej: 51913048384)
-         if s.get("pipeline_stage") != new_stage:
+             telefono = wa_id
-             s["pipeline_stage"] = new_stage
+             try:
-             synced += 1
+                 pedidos_encontrados = buscar_pedido_por_telefono(telefono)
-     return {"ok": True, "synced": synced}
+                 if pedidos_encontrados:
- 
+                     s["datos_pedido"] = pedidos_encontrados[0]
- @app.get("/api/pipeline/scan-orders")
+                     s["pedidos_multiples"] = pedidos_encontrados
- async def api_pipeline_scan_orders(request: Request):
+                     fetched += 1
-     if not verificar_sesion(request):
+             except Exception as _e:
-         raise HTTPException(status_code=403, detail="No autorizado")
+                 print(f"[SYNC] Error buscando pedido para {wa_id}: {_e}")
-     if not es_admin(request):
+         
-         raise HTTPException(status_code=403, detail="Solo administradores")
+         eg = (s.get("datos_pedido") or {}).get("estadoGeneral", "")
-     try:
+         new_stage = next(
-         from firebase_client import scan_estadosgenerales_bd
+             (st["id"] for st in global
… [diff truncated]
- **[problem-fix] Fixed null crash in Config — prevents null/undefined runtime crashes**: -         // --- Config Modal ---
+         // --- Config Modal + Drag & Drop Setup ---
-             document.getElementById('btnConfig').onclick = () => {
+             // Show drag & drop toggle for admins
-                 renderStagesList();
+             document.getElementById('dndToggleWrap').classList.add('visible');
-                 document.getElementById('configModal').style.display = 'flex';
+ 
-             };
+             document.getElementById('btnConfig').onclick = () => {
-         }
+                 renderStagesList();
- 
+                 document.getElementById('configModal').style.display = 'flex';
-         function closeConfigModal() {
+             };
-             document.getElementById('configModal').style.display = 'none';
+         }
-             window.location.reload(); // Reload to see changes
+ 
-         }
+         // =====[REDACTED]
- 
+         // DRAG & DROP (admin only, off by default)
-         function renderStagesList() {
+         // =====[REDACTED]
-             const list = document.getElementById('stagesList');
+         let dndEnabled = false;
-             list.innerHTML = '';
+         let dragCard = null;        // the card element being dragged
-             STAGES.sort((a,b) => (a.order||0) - (b.order||0));
+         let dragWaId = null;        // wa_id of the card
- 
+         let dropToast = null;
-             STAGES.forEach((st, idx) => {
+ 
-                 const div = document.createElement('div');
+         function toggleDnd() {
-                 div.className = 'stage-item';
+             dndEnabled = document.getElementById('dndToggle').checked;
-                 div.draggable = true;
+             document.body.classList.toggle('dnd-active', dndEnabled);
-                 div.dataset.id = st.id;
+             // Re-bind draggable attribute on all cards
-                 
+             document.querySelectorAll('.pipeline-card').forEach(ca
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in settings.html**: - </html>
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in perfil.html**: - 
+ 
- 
+ 

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Reload — prevents null/undefined runtime crashes**: -             document.getElementById('btnSync').style.display = 'none';
+         } else {
-         } else {
+             document.getElementById('btnConfig').onclick = () => {
-             document.getElementById('btnConfig').onclick = () => {
+                 renderStagesList();
-                 renderStagesList();
+                 document.getElementById('configModal').style.display = 'flex';
-                 document.getElementById('configModal').style.display = 'flex';
+             };
-             };
+         }
-         }
+ 
- 
+         function closeConfigModal() {
-         async function syncPipeline() {
+             document.getElementById('configModal').style.display = 'none';
-             const btn = document.getElementById('btnSync');
+             window.location.reload(); // Reload to see changes
-             const origText = btn.innerHTML;
+         }
-             btn.disabled = true;
+ 
-             btn.style.opacity = '0.6';
+         function renderStagesList() {
-             btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation:spin 1s linear infinite"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg> Sincronizando...`;
+             const list = document.getElementById('stagesList');
-             try {
+             list.innerHTML = '';
-                 const res = await fetch('/api/pipeline/sync', {method: 'POST'});
+             STAGES.sort((a,b) => (a.order||0) - (b.order||0));
-                 const data = await res.json();
+ 
-                 if (data.ok) {
+             STAGES.forEach((st, idx) => {
-                     showToast(`Sincronización completa: ${data.synced} sesiones actualizadas, ${data.fetched_orders} pedidos recuperados.`);
+                 cons
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html, deleteStage]
- **[problem-fix] Fixed null crash in Sincronizando — prevents null/undefined runtime crashes**: -         } else {
+             document.getElementById('btnSync').style.display = 'none';
-             document.getElementById('btnConfig').onclick = () => {
+         } else {
-                 renderStagesList();
+             document.getElementById('btnConfig').onclick = () => {
-                 document.getElementById('configModal').style.display = 'flex';
+                 renderStagesList();
-             };
+                 document.getElementById('configModal').style.display = 'flex';
-         }
+             };
- 
+         }
-         function closeConfigModal() {
+ 
-             document.getElementById('configModal').style.display = 'none';
+         async function syncPipeline() {
-             window.location.reload(); // Reload to see changes
+             const btn = document.getElementById('btnSync');
-         }
+             const origText = btn.innerHTML;
- 
+             btn.disabled = true;
-         function renderStagesList() {
+             btn.style.opacity = '0.6';
-             const list = document.getElementById('stagesList');
+             btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="animation:spin 1s linear infinite"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg> Sincronizando...`;
-             list.innerHTML = '';
+             try {
-             STAGES.sort((a,b) => (a.order||0) - (b.order||0));
+                 const res = await fetch('/api/pipeline/sync', {method: 'POST'});
- 
+                 const data = await res.json();
-             STAGES.forEach((st, idx) => {
+                 if (data.ok) {
-                 const div = document.createElement('div');
+                     showToast(`Sincronización completa: ${data.synced} sesiones actualizadas, ${data.f
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] 🟢 Edited document_loader.py (5 changes, 221min)**: Active editing session on document_loader.py.
5 content changes over 221 minutes.
