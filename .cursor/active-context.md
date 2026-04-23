> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `server.py` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
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
- **[problem-fix] problem-fix in server.py**: -     for l in global_labels:
+     for l in labels_for_line:

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[convention] Patched security issue Request — parallelizes async operations for speed — confirmed 3x**: - @app.get("/api/admin/stats")
+ @app.get("/api/admin/debug_sessions")
- async def get_admin_stats(request: Request, line_id: str = "all"):
+ async def debug_sessions(request: Request):
-     """Devuelve las estadísticas de chats según la línea solicitada."""
+     """TEMPORAL: Muestra los lineId en memoria para diagnosticar el filtro."""
-         
+     resultado = []
-     respondidos = 0
+     for wa_id, s in list(sesiones.items())[:50]:  # máx 50 para no saturar
-     por_responder = 0
+         s_line = s.get("lineId", "") or ""
-     pendientes_bot = 0
+         if s_line and str(s_line).isdigit():
-     pendientes_asesor = 0
+             s_line = "principal (normalizado)"
-     
+         if not s_line:
-     for wa_id, s in sesiones.items():
+             parts = wa_id.rsplit("_", 1)
-         # Intentar obtener lineId desde el campo guardado
+             if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) >= 8:
-         s_line = s.get("lineId", "") or ""
+                 s_line = f"{parts[0]} (inferido)"
-         
+             else:
-         # Normalizar IDs numéricos de Meta → siempre son la línea principal
+                 s_line = "principal (default)"
-         if s_line and str(s_line).isdigit():
+         resultado.append({
-             s_line = "principal"
+             "session_key": wa_id,
-         
+             "lineId_stored": s.get("lineId", "⚠️ VACÍO"),
-         # Si no tiene lineId, intentar inferirlo desde la session key compuesta (ej: "qr_ventas_1_519...")
+             "lineId_effective": s_line,
-         if not s_line:
+             "unread": s.get("unread_count", 0),
-             parts = wa_id.rsplit("_", 1)
+             "bot_activo": s.get("bot_activo", False)
-             # Las claves compuestas tienen formato "lineId_numeroWA"
+         })
-             # Si la parte derecha es numérica larga → es el número de teléfono
+     return JSONResponse({"total": len(sesiones),
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] 🟢 Edited document_loader.py (5 changes, 221min)**: Active editing session on document_loader.py.
5 content changes over 221 minutes.
- **[convention] Fixed null crash in Determinar — prevents null/undefined runtime crashes — confirmed 3x**: -                 // Determinar la l\u00ednea activa: del chat abierto o del filtro de inbox
+             try {
-                 const line_id = window.ACTIVE_CHAT_LINE
+                 // Determinar la l\u00ednea activa: del chat abierto o del filtro de inbox
-                     || new URLSearchParams(window.location.search).get('line')
+                 const line_id = window.ACTIVE_CHAT_LINE
-                     || 'principal';
+                     || new URLSearchParams(window.location.search).get('line')
- 
+                     || 'principal';
-                 const res = await fetch("/api/admin/labels/save", {
+ 
-                     method: "POST",
+                 const res = await fetch("/api/admin/labels/save", {
-                     headers: { "Content-Type": "application/json" },
+                     method: "POST",
-                     body: JSON.stringify({ id: id, name: name, color: color, line_id: line_id })
+                     headers: { "Content-Type": "application/json" },
-                 });
+                     body: JSON.stringify({ id: id, name: name, color: color, line_id: line_id })
-                 if (res.ok) {
+                 });
-                     document.getElementById("createLabelModal").style.display = "none";
+                 if (res.ok) {
-                     window.location.reload();
+                     document.getElementById("createLabelModal").style.display = "none";
-                 } else {
+                     window.location.reload();
-                     alert("Error guardando etiqueta (Respuesta del servidor).");
+                 } else {
-                 }
+                     alert("Error guardando etiqueta (Respuesta del servidor).");
-             } catch (e) {
+                 }
-                 alert("Error guardando etiqueta (Conectividad).");
+             } catch (e) {
-             }
+                 alert("Error guardando etiqueta (Conec
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in inbox.html**: -             width: clamp(280px, 30vw, 510px);
+             width: clamp(280px, 30vw, 650px);

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 4x**: -             width: clamp(280px, 30vw, 460px);
+             width: clamp(280px, 30vw, 510px);

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Soft — prevents null/undefined runtime crashes — confirmed 3x**: -                     
+                     const line = urlParams.get('line') || sessionStorage.getItem('inboxLineFilter') || 'all';
-                     // Soft Virtual Exit to instantly clear chat UI without reloading
+                     
-                     window.history.replaceState(null, '', `/inbox?tab=${tab}`);
+                     // Soft Virtual Exit to instantly clear chat UI without reloading
-                     
+                     const lineParam = line !== 'all' ? `&line=${line}` : '';
-                     document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
+                     window.history.replaceState(null, '', `/inbox?tab=${tab}${lineParam}`);
-                     const viewer = document.querySelector('.chat-viewer-panel');
+                     document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
-                     if (viewer) {
+                     
-                         viewer.innerHTML = `
+                     const viewer = document.querySelector('.chat-viewer-panel');
-                         <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
+                     if (viewer) {
-                             <h3>Bandeja de Entrada</h3>
+                         viewer.innerHTML = `
-                             <p style="font-size:0.9rem; max-width:400px; text-align:center;">Selecciona una conversación para empezar o continuar chateando.</p>
+                         <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
-                         </div>`;
+                             <h3>Bandeja de Entrada</h3>
-                     }
+                             <p style="font-size:0.9rem; max-width:400px; text-align:
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
