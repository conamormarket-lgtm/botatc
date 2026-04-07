> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

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
- **[convention] what-changed in inbox.html — confirmed 4x**: -             width: 280px;
+             width: 340px;

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] 🟢 Edited settings.html (1267 changes, 5min)**: Active editing session on settings.html.
1267 content changes over 5 minutes.
- **[convention] what-changed in settings.html — confirmed 6x**: -             --bg-main: #5574bb;
+             --bg-main: #0f172a;

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Configuraci — wraps unsafe operation in error boundary — confirmed 5x**: - <head>
+ 
-     <meta charset="UTF-8">
+ <head>
-     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
+     <meta charset="UTF-8">
-     <title>Configuración de Agente IA - IA-ATC</title>
+     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
-     <!-- Fuentes de Google -->
+     <title>Configuración de Agente IA - IA-ATC</title>
-     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
+     <!-- Fuentes de Google -->
-     <style>
+     <link
-         :root {
+         href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
-             /* 1. Nivel de Color Principal */
+         rel="stylesheet">
-             --primary-color: #3b82f6;       
+     <style>
-             --primary-hover: #2563eb;       
+         :root {
-             /* 2. Nivel de Color de Acento */
+             /* 1. Nivel de Color Principal */
-             --accent-bg: #1e293b;           
+             --primary-color: #3b82f6;
-             --accent-border: #334155;       
+             --primary-hover: #2563eb;
-             --accent-hover-soft: #334155;   
+             /* 2. Nivel de Color de Acento */
-             /* 3. Nivel de Color de Fondo General */
+             --accent-bg: #1e293b;
-             --bg-main: #6278ac;             
+             --accent-border: #334155;
-             /* 4. Tipografías */
+             --accent-hover-soft: #334155;
-             --font-main: 'Inter', sans-serif;
+             /* 3. Nivel de Color de Fondo General */
-             --font-heading: 'Outfit', sans-serif;
+             --bg-main: #5574bb;
-             --font-mono: 'JetBrains Mono', monospace;
+             /* 4. Tipografías */
-             /* Otros */
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] 🟢 Edited check_js2.py (9 changes, 355min)**: Active editing session on check_js2.py.
9 content changes over 355 minutes.
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
