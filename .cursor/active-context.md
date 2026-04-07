> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `settings.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Actualizar — prevents null/undefined runtime crashes**: -                 }
+                     if(typeof window.aplicarFiltroChats === 'function') {
-                 
+                         window.aplicarFiltroChats();
-                 // Actualizar visibilidad de Chat
+                     }
-                 const newScroll = doc.getElementById('chatScroll');
+                 }
-                 const oldScroll = document.getElementById('chatScroll');
+                 
-                 if(newScroll && oldScroll) {
+                 // Actualizar visibilidad de Chat
-                     if (oldScroll.innerHTML !== newScroll.innerHTML) {
+                 const newScroll = doc.getElementById('chatScroll');
-                         // Respetar scroll solo si el usuario no ha subido a leer
+                 const oldScroll = document.getElementById('chatScroll');
-                         const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
+                 if(newScroll && oldScroll) {
-                         oldScroll.innerHTML = newScroll.innerHTML;
+                     if (oldScroll.innerHTML !== newScroll.innerHTML) {
-                         if(isAtBottom) {
+                         // Respetar scroll solo si el usuario no ha subido a leer
-                             oldScroll.scrollTop = oldScroll.scrollHeight;
+                         const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
-                         }
+                         oldScroll.innerHTML = newScroll.innerHTML;
-                     }
+                         if(isAtBottom) {
-                 }
+                             oldScroll.scrollTop = oldScroll.scrollHeight;
-             } catch (e) {
+                         }
-                 console.warn('Error en Live Chat Polling:', e);
+                     }
-             }
+                 }
-         }, 1500);
+             } catch (e) 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]

### 📐 Generic Logic Conventions & Fixes
- **[what-changed] 🟢 Edited check_js2.py (9 changes, 355min)**: Active editing session on check_js2.py.
9 content changes over 355 minutes.
- **[problem-fix] Fixed null crash in Custom — prevents null/undefined runtime crashes**: -     </style>
+     
- </head>
+         /* Custom Scrollbar for all */
- <body class="{body_class}">
+         ::-webkit-scrollbar {
- 
+             width: 8px;
-     <!-- 1. BARRA LATERAL IZQUIERDA (Navegación Desktop / Bottom Mobile) -->
+             height: 8px;
-     <nav class="sidebar-nav">
+         }
-         <!-- Inbox Icon -->
+         ::-webkit-scrollbar-track {
-         <a href="/inbox" class="nav-item active" title="Bandeja de Entrada (Inbox)">
+             background: transparent; 
-             <svg viewBox="0 0 24 24"><path d="M22 12h-6l-2 3h-4l-2-3H2" /><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" /></svg>
+         }
-         </a>
+         ::-webkit-scrollbar-thumb {
-         <!-- Agent Settings Icon -->
+             background: var(--accent-border); 
-         <a href="/settings" class="nav-item" title="Personalizar Agente IA">
+             border-radius: 4px;
-             <svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
+         }
-         </a>
+         ::-webkit-scrollbar-thumb:hover {
-         <!-- System Settings Icon -->
+             background: var(--text-muted); 
-         <a href="/admin" class="nav-item" title="Panel Clásico Anterior">
+         }
-             <svg viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
+ 
-         </a>
+ </style>
- 
+ </head>
-         <!-- Indicador global abajo -->
+ <body class="{body_class}">
-         <div class="bot-status-indicator" title="Estado Global del Bot"></div>
+ 
-     </nav>
+     <!-- 1. BARRA LATERAL IZQUIERDA (Navegación Desktop / Bottom Mobile) -->
- 
+     <nav class="sidebar-nav">
-     <!-- 2. PANEL CENTRAL (Lista de Chats) -->
+         <!-- Inbox Icon -->
-     <div class="chat-
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Flotante — parallelizes async operations for speed**: -                     <!-- Menú Flotante de Emojis -->
+                     <!-- Menú Flotante Unificado (Emojis + Stickers) -->
-                     <div id="emojiMenu" style="display:none; position:absolute; bottom:55px; left:0; z-index:1000; background:transparent; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.15);">
+                     <div id="emojiMenu" style="display:none; position:absolute; bottom:55px; left:0; z-index:1000; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.3); flex-direction:column; width:340px; overflow:hidden;">
-                         <emoji-picker class="light"></emoji-picker>
+                         <div style="display:flex; background:var(--accent-bg); border-bottom:1px solid var(--accent-border);">
-                     </div>
+                             <button type="button" onclick="document.getElementById('emojiTabContent').style.display='block'; document.getElementById('stickerTabContent').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.color='var(--primary-color)'; this.nextElementSibling.style.borderBottom='none'; this.nextElementSibling.style.color='var(--text-muted)';" style="flex:1; padding:0.8rem; background:transparent; border:none; border-bottom:2px solid var(--primary-color); color:var(--primary-color); cursor:pointer; font-weight:600; font-size:0.9rem; transition:color 0.2s;">🙂 Emojis</button>
- 
+                             <button type="button" onclick="document.getElementById('stickerTabContent').style.display='block'; document.getElementById('emojiTabContent').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.color='var(--primary-color)'; this.previousElementSibling.style.borderBottom='none'; this.previousElementSibling.style.color='var(--text-muted)'; cargarStickers();" style="flex:1; padding:0.8rem; background:transparent; border:no
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in POST — parallelizes async operations for speed — confirmed 4x**: -                     let finalMsg;
+                     if(msgType === 'action_label') {{
-                     if(msgType === 'text') {{
+                         if (msgObj.media_id) {{
-                         finalMsg = (msgObj.content || '').replace(/#nombre/gi, nombreCliente);
+                             try {{
-                     }} else if(msgType === 'image') {{
+                                 await fetch("/api/admin/chats/labels/toggle", {{
-                         finalMsg = `[imagen:${{msgObj.media_id}}]`;
+                                     method: "POST",
-                     }} else if(msgType === 'video') {{
+                                     headers: {{"Content-Type":"application/json"}},
-                         finalMsg = `[video:${{msgObj.media_id}}]`;
+                                     body: JSON.stringify({{ wa_id: "{wa_id}", label_id: msgObj.media_id }})
-                     }} else if(msgType === 'audio') {{
+                                 }});
-                         finalMsg = `[audio:${{msgObj.media_id}}]`;
+                             }} catch(e) {{}}
-                     }} else {{
+                         }}
-                         finalMsg = msgObj.content || '';
+                         if (i < msgs.length - 1) await new Promise(r => setTimeout(r, delay / 2));
-                     }}
+                         continue;
-                     
+                     }}
-                     if(!finalMsg) {{ i < msgs.length-1 && await new Promise(r=>setTimeout(r, delay)); continue; }}
+ 
-                     
+                     let finalMsg;
-                     const endsWithSlash = input.value.trimEnd().endsWith("/");
+                     if(msgType === 'text') {{
-                     input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
+                         finalMsg = (msgObj.content || '').replace(/#nombre/gi, nombr
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] Fixed null crash in Title — prevents null/undefined runtime crashes — confirmed 5x**: -                     container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
+                     container.style.cssText = "display:flex; flex-direction:column; background:var(--accent-bg); padding:0.65rem 0.75rem; border-radius:8px; border:1px solid var(--accent-border); transition:border-color 0.15s; position:relative;";
-                     btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column;";
+                     btn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); width:100%; display:flex; flex-direction:column; gap:0.25rem;";
-                     const headerRow = document.createElement("div");
+                     // Title row
-                     headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:0.2rem;";
+                     const headerRow = document.createElement("div");
-                     const titleWrap = document.createElement("div");
+                     headerRow.style.cssText = "display:flex; justify-content:space-between; align-items:center; width:100%;";
-                     titleWrap.style.cssText = "display:flex; align-items:center; gap:0.5rem;";
+                     const titleWrap = document.createElement("div");
-                     const titleEl = document.createElement("strong");
+                     titleWrap.style.cssText = "display:flex; align-items:center; gap:0.4rem; flex-wrap:wrap;";
-                     titleEl.innerText = qr.title || qr.category || '(sin título)';
+                     const titleEl = document.createElement("strong");
-                     titleEl.style.fontSize = "0.9rem";
+                     t
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in dump.html**: -                     const slashMatch = input.value.match(/(?:^|\\s)\\/$/); 
+                     const endsWithSlash = input.value.trimEnd().endsWith("/");
-                     if (slashMatch) {
+                     if (endsWithSlash) {

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in server.py**: -                     const slashMatch = input.value.match(/(?:^|\\\\s)\\\\/$/); 
+                     const endsWithSlash = input.value.trimEnd().endsWith("/");
-                     if (slashMatch) {{
+                     if (endsWithSlash) {{

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[problem-fix] problem-fix in patcher.py**: - """
+ """Fix the broken regex line"""
- FINAL FIX: Completely rewrite the broken section of server.py
+ code = open('server.py', 'r', encoding='utf-8').read()
- The JS code is broken across lines without proper <script> tags.
+ 
- """
+ # The broken regex line - find it and replace it
- 
+ old = "                    const slashMatch = input.value.match(/(?:^|\\\\\\\\s)\\\\\\\\/$/); \r\n                    if (slashMatch) {{"
- code = open('server.py', 'r', encoding='utf-8').read()
+ new = "                    const endsWithSlash = input.value.trimEnd().endsWith(\"/\");\r\n                    if (endsWithSlash) {{"
- # The broken section starts with the orphan JS sticking to </div>
+ if old in code:
- BROKEN_START = """            <!-- END RIGHT SIDEBAR -->
+     code = code.replace(old, new)
-         </div>            let isSendingSequence = false;
+     print("Fixed regex line!")
-             
+ else:
-             async function aplicarQuickReply(qrId) {{"""
+     # Try without \r
- 
+     old2 = old.replace('\r\n', '\n')
- BROKEN_END = """            function checkQuickReplyTrigger(input) {{"""
+     new2 = new.replace('\r\n', '\n')
- 
+     if old2 in code:
- # Verify positions
+         code = code.replace(old2, new2)
- si = code.find(BROKEN_START)
+         print("Fixed regex line (LF)!")
- ei = code.find(BROKEN_END)
+     else:
- print(f"Broken section start: {si}")
+         # Find the line another way
- print(f"checkQuickReplyTrigger starts at: {ei}")
+         lines = code.split('\n')
- 
+         for i, line in enumerate(lines):
- if si == -1:
+             if 'slashMatch' in line and 'regex' not in line:
-     print("ERROR: Could not find broken section start")
+                 print(f"Found at line {i+1}: {repr(line)}")
-     exit(1)
+                 lines[i] = '                    const endsWithSlash = input.value.trimEnd().endsWith("/");'
- 
+                 # Fix next line too
- # We'll replace everything from BROKEN_START up to (but not inclu
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [code, old, new, code, old2]
- **[convention] Fixed null crash in RESPONSIVE — prevents null/undefined runtime crashes — confirmed 3x**: - 
+         .bubble { max-width:80%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; }
-         /* ==================================================
+         .lado-izq { align-self:flex-start; }
-            RESPONSIVE DESIGN (MÓVIL / TABLET)
+         .lado-der { align-self:flex-end; }
-            ================================================== */
+         .bubble-bot { background:var(--accent-bg); color:var(--text-main); border-bottom-left-radius:4px; border:1px solid var(--accent-border); }
-         @media (max-width: 768px) {
+         .bubble-user { background:var(--primary-color); color:#ffffff; border-bottom-right-radius:4px; }
-             body {
+         
-                 flex-direction: column;
+ 
-             }
+         /* ==================================================
-             
+            RESPONSIVE DESIGN (MÓVIL / TABLET)
-             /* Sidebar se convierte en Bottom Navigation Bar */
+            ================================================== */
-             .sidebar-nav {
+         @media (max-width: 768px) {
-                 flex-direction: row;
+             body {
-                 width: 100%;
+                 flex-direction: column;
-                 height: 65px;
+             }
-                 padding: 0;
+             
-                 border-right: none;
+             /* Sidebar se convierte en Bottom Navigation Bar */
-                 border-top: 1px solid var(--accent-border);
+             .sidebar-nav {
-                 order: 3; /* Al final de la columna */
+                 flex-direction: row;
-                 justify-content: space-around;
+                 width: 100%;
-                 background-color: var(--bg-main); /* para tapar info detrás si es necesario */
+                 height: 65px;
-             }
+                 padding: 0;
-             .nav-item { margin-bottom: 0; }
+                 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in None — prevents null/undefined runtime crashes — confirmed 3x**: -             </form>
+             </form>            """
-             
+ 
-             <script>
+         session_tags = s.get("etiquetas", [])
-             let quickRepliesCache = [];
+         if session_tags is None: session_tags = []
-             async function cargarQuickReplies() {{
+         tags_bar = ""
-                 const list = document.getElementById("quickRepliesList");
+         for tid in session_tags:
-                 if(!list) return;
+             lbl = next((l for l in global_labels if l.get("id") == tid), None)
-                 list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando respuestas...</div>`;
+             if lbl:
-                 try {{
+                 col = lbl.get("color", "#94a3b8")
-                     const res = await fetch("/api/quick-replies");
+                 nm = lbl.get("name", "Etiqueta")
-                     if (!res.ok) throw new Error("HTTP " + res.status);
+                 tags_bar += f'<span style="background:{col}22; color:{col}; font-size:0.65rem; padding:0.15rem 0.4rem; border-radius:4px; font-weight:600; border: 1px solid {col}44;">{nm}</span>'
-                     const data = await res.json();
+ 
-                     quickRepliesCache = data;
+         chat_viewer_html = f"""
-                     renderQuickReplies(data);
+         <div style="display:flex; flex-direction:row; height:100%; width:100%;">
-                 }} catch(e) {{
+             <!-- START CHAT MAIN COLUMN -->
-                     list.innerHTML = `<div style="font-size:0.85rem; color:red; padding:1rem; text-align:center; background:rgba(255,0,0,0.1); border-radius:8px;">Error: ${{e.message}}</div>`;
+             <div style="flex:1; display:flex; flex-direction:column; min-width:0; background:var(--bg-main);">
-                 }}
+                 {status_bar}
-             }}
+                 <div style="padding:1.5rem;border-bottom:
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
