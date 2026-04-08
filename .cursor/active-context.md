> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in Content — prevents null/undefined runtime crashes**: -             const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : '';
+             const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
-                 await fetch('/enviar_mensaje', {
+                 const res = await fetch('/api/admin/enviar_manual', {
-                     headers: {'Content-Type': 'application/x-www-form-urlencoded'},
+                     headers: { 'Content-Type': 'application/json' },
-                     body: `wa_id=${wa_id}&mensaje=${encodeURIComponent(msj)}&reply_to=${replyToWamid}`
+                     body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
-             } catch(e) {
+                 
-                 console.error("Error direct send", e);
+                 const data = await res.json();
-             }
+                 if(!data.ok) { console.error("Error direct send json", data); }
-         };
+             } catch(e) {
- 
+                 console.error("Error direct send", e);
-         window.enviarMensajeManual = async function (e, wa_id) {
+             }
-             e.preventDefault();
+         };
-             const input = document.getElementById('manualMsgInput');
+ 
-             if (!input) return;
+         window.enviarMensajeManual = async function (e, wa_id) {
-             const msj = input.value.trim();
+             e.preventDefault();
-             if (!msj) return;
+             const input = document.getElementById('manualMsgInput');
- 
+             if (!input) return;
-             // Vaciar y enfocar
+             const msj = input.value.trim();
-             input.value = '';
+             if (!msj) return;
-             input.focus();
+ 
- 
+             // Vaciar y enfocar
-             // Dibujado optimista instantáneo
+             input.value = '';
-             const scroll = document.getE
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in POST — prevents null/undefined runtime crashes — confirmed 3x**: -         window.enviarMensajeManual = async function (e, wa_id) {
+         
-             e.preventDefault();
+         window.enviarMensajeDirecto = async function(wa_id, msj) {
-             const input = document.getElementById('manualMsgInput');
+             if (!msj) return;
-             if (!input) return;
+             const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : '';
-             const msj = input.value.trim();
+             try {
-             if (!msj) return;
+                 await fetch('/enviar_mensaje', {
- 
+                     method: 'POST',
-             // Vaciar y enfocar
+                     headers: {'Content-Type': 'application/x-www-form-urlencoded'},
-             input.value = '';
+                     body: `wa_id=${wa_id}&mensaje=${encodeURIComponent(msj)}&reply_to=${replyToWamid}`
-             input.focus();
+                 });
- 
+             } catch(e) {
-             // Dibujado optimista instantáneo
+                 console.error("Error direct send", e);
-             const scroll = document.getElementById('chatScroll');
+             }
-             if (scroll) {
+         };
-                 const bubble = document.createElement('div');
+ 
-                 bubble.className = "bubble bubble-bot lado-izq";
+         window.enviarMensajeManual = async function (e, wa_id) {
-                 bubble.style.border = "1px solid var(--primary-color)";
+             e.preventDefault();
-                 bubble.innerText = msj;
+             const input = document.getElementById('manualMsgInput');
-                 scroll.appendChild(bubble);
+             if (!input) return;
-                 scroll.scrollTop = scroll.scrollHeight;
+             const msj = input.value.trim();
-             }
+             if (!msj) return;
-             const replyWamid = document.getElementById('replyToWamid') ? document.getElementById(
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] Updated schema Intercept**: -         // Smart ESC to exit chat without interrupting sequence
+         
-         document.addEventListener('keydown', function(event) {
+         // Intercept clicks on other chats if a sequence is sending
-             if (event.key === 'Escape') {
+         document.addEventListener('click', async function(e) {
-                 if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
+             const chatRow = e.target.closest('.chat-row');
-                     const urlParams = new URLSearchParams(window.location.search);
+             if (chatRow && window.isSendingSequence) {
-                     const tab = urlParams.get('tab') || 'all';
+                 e.preventDefault();
-                     
+                 const url = chatRow.href;
-                     if (window.isSendingSequence) {
+                 
-                         // Soft Virtual Exit to keep sequence sending in background
+                 // Soft Navigation (PJAX style)
-                         window.history.pushState(null, '', `/inbox?tab=${tab}`);
+                 window.history.pushState(null, '', url);
-                         
+                 document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
-                         document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
+                 chatRow.classList.add('active-row');
-                         
+                 
-                         const viewer = document.querySelector('.chat-viewer-panel');
+                 const viewer = document.querySelector('.chat-viewer-panel');
-                         if (viewer) {
+                 if (viewer) {
-                             viewer.innerHTML = `
+                     viewer.innerHTML = '<div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; 
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] Updated schema Smart**: -         // Pure ESC to exit chat
+         // Smart ESC to exit chat without interrupting sequence
-                     window.location.href = `/inbox?tab=${tab}`;
+                     
-                 }
+                     if (window.isSendingSequence) {
-             }
+                         // Soft Virtual Exit to keep sequence sending in background
-         });
+                         window.history.pushState(null, '', `/inbox?tab=${tab}`);
- 
+                         
- </script>
+                         document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
-                 </div>
+                         
- 
+                         const viewer = document.querySelector('.chat-viewer-panel');
-                 <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
+                         if (viewer) {
-                     <button type="button" onclick="document.getElementById('createLabelModal').style.display='none'"
+                             viewer.innerHTML = `
-                         style="padding:0.6rem 1rem; border-radius:6px; background:none; border:none; color:var(--text-main); font-weight:600; cursor:pointer;">Cancelar</button>
+                             <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
-                     <button type="button" onclick="guardarNuevaEtiquetaModal()"
+                                 <h3>Bandeja de Entrada</h3>
-                         style="padding:0.6rem 1rem; border-radius:6px; background:var(--primary-color); border:none; color:white; font-weight:600; cursor:pointer;">Guardar</button>
+                                 <p style="font-size:0.9rem; max-width:400px;">Selecciona una conversación para empezar o continuar chateando.</p>
-                 </div>
+                             </div>`;
-          
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in inbox.html**: -             --bg-sidebar: #17264a;
+             --bg-sidebar: var(--bg-main);
-             --bg-list: #1b2d56;
+             --bg-list: var(--bg-main);

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in LEFT — prevents null/undefined runtime crashes — confirmed 4x**: -             background-color: var(--bg-main);
+             background-color: var(--bg-sidebar);
-         
+         }
-             background-color: var(--bg-sidebar);}
+ 
- 
+         .chat-list-panel {
-         .chat-list-panel {
+             width: 340px;
-             width: 340px;
+             background-color: var(--bg-list);
-             background-color: var(--bg-main);
+             border-right: 1px solid var(--accent-border);
-             border-right: 1px solid var(--accent-border);
+             display: flex;
-             display: flex;
+             flex-direction: column;
-             flex-direction: column;
+             z-index: 5;
-             z-index: 5;
+             transition: all 0.3s ease;
-             transition: all 0.3s ease;
+             min-height: 0;
-             min-height: 0;
+         }
-         
+ 
-             background-color: var(--bg-list);}
+         .chat-viewer-panel {
- 
+             flex: 1;
-         .chat-viewer-panel {
+             background-color: var(--bg-main);
-             flex: 1;
+             display: flex;
-             background-color: var(--bg-main);
+             flex-direction: column;
-             display: flex;
+             position: relative;
-             flex-direction: column;
+             min-width: 0;
-             position: relative;
+             /* previene desbordamiento en flex */
-             min-width: 0;
+         }
-             /* previene desbordamiento en flex */
+ 
-         }
+         /* ---------------- LEFT SIDEBAR ---------------- */
- 
+         .nav-item {
-         /* ---------------- LEFT SIDEBAR ---------------- */
+             width: 44px;
-         .nav-item {
+             height: 44px;
-             width: 44px;
+             border-radius: 12px;
-             height: 44px;
+             display: flex;
-             border-radius: 12px;
+             align-items: center;
-             
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 5x**: -             --bg-main: #1b2b4e;             
+             --bg-main: #213668;             

📌 IDE AST Context: Modified symbols likely include [html]
- **[decision] decision in inbox.html**: -             --primary-hover: #527ddb;
+             --primary-hover: #2857bd;
-             --accent-bg: #374a68;
+             --accent-bg: #1e293b;

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 7x**: -             --accent-bg: #5173aa;
+             --accent-bg: #364e75;

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] decision in inbox.html — confirmed 9x**: -             --primary-hover: #2857bd;
+             --primary-hover: #527ddb;

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Inbox — prevents null/undefined runtime crashes — confirmed 11x**: - <head>
+ 
-     <meta charset="UTF-8">
+ <head>
-     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
+     <meta charset="UTF-8">
-     <title>Inbox - IA-ATC</title>
+     <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
-     <!-- Fuentes de Google: Inter para lectura, Outfit para acentos audaces -->
+     <title>Inbox - IA-ATC</title>
-     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet">
+     <!-- Fuentes de Google: Inter para lectura, Outfit para acentos audaces -->
-     <script type="module" src="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js"></script>
+     <link
-     <style>
+         href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Plus+Jakarta+Sans:wght@600;700&display=swap"
-         :root {
+         rel="stylesheet">
-             /* 1. Nivel de Color Principal */
+     <script type="module" src="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js"></script>
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
-             --bg-main: #1b2b4e;             
+             --accent-border: #334155;
-             /* 4. Tipografías */
+             --accent-hover-soft: #334155;
-             --font-main: 'Inter', sans-serif;
+     
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] 🟢 Edited inbox.html (4071 changes, 24min)**: Active editing session on inbox.html.
4071 content changes over 24 minutes.
- **[trade-off] trade-off in inbox.html**: -             --bg-main: #0f172a;             
+             --bg-main: #213668;             
- </script>
+ 
-                 </div>
+         // Pure ESC to exit chat
-                 
+         document.addEventListener('keydown', function(event) {
-                 <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
+             if (event.key === 'Escape') {
-                     <button type="button" onclick="document.getElementById('createLabelModal').style.display='none'" style="padding:0.6rem 1rem; border-radius:6px; background:none; border:none; color:var(--text-main); font-weight:600; cursor:pointer;">Cancelar</button>
+                 if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
-                     <button type="button" onclick="guardarNuevaEtiquetaModal()" style="padding:0.6rem 1rem; border-radius:6px; background:var(--primary-color); border:none; color:white; font-weight:600; cursor:pointer;">Guardar</button>
+                     const urlParams = new URLSearchParams(window.location.search);
-                 </div>
+                     const tab = urlParams.get('tab') || 'all';
-             </div>
+                     window.location.href = `/inbox?tab=${tab}`;
-         </div>
+                 }
-     </div>
+             }
- 
+         });
-     <!-- Elementos ocultos para selectores del sistema -->
+ 
-     <input type="file" id="hiddenFileInput" style="display:none;" accept="image/*">
+ </script>
- </body>
+                 </div>
- </html>
+                 
- 
+                 <div style="display:flex; justify-content:flex-end; gap:0.5rem;">
+                     <button type="button" onclick="document.getElementById('createLabelModal').style.display='none'" style="padding:0.6rem 1rem; border-radius:6px; background:none; border:none; color:var(--text-main); font-weight:600; cursor:pointer;">Cancelar</button>
+                     <button t
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in NAVEGACI — prevents null/undefined runtime crashes — confirmed 5x**: -     <script type="module" src="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js">// Si no se cerró ningún menú y estamos dentro de un chat, ir al inicio
+     <script type="module" src="https://cdn.jsdelivr.net/npm/emoji-picker-element@^1/index.js">
-                 if(!closedModal && window.location.pathname.match(/^\/inbox\/.+/)) {
+         // --- NAVEGACIÓN Y SKELETONS ---
-                     const urlParams = new URLSearchParams(window.location.search);
+         document.addEventListener('keydown', function(event) {
-                     const tab = urlParams.get('tab') || 'all';
+             if (event.key === 'Escape') {
-                     window.location.href = `/inbox?tab=${tab}`;
+                 let closedModal = false;
-                 }
+                 ['qrCreateModal', 'rightSidebar', 'emojiMenu', 'attachMenu', 'inboxFilterMenu', 'bubbleContextMenu'].forEach(id => {
-             }
+                     const el = document.getElementById(id);
-         });
+                     if(el && el.style.display !== 'none' && el.style.display !== '') {
- 
+                         el.style.display = 'none';
-         document.addEventListener('click', function(e) {
+                         closedModal = true;
-             const chatRow = e.target.closest('a.chat-row');
+                     }
-             if(chatRow) {
+                 });
-                 const chatViewer = document.querySelector('.chat-viewer-panel');
+                 
-                 if(chatViewer) {
+                 // Si no se cerró ningún menú y estamos dentro de un chat, ir al inicio
-                     // Muestra el skeleton layout simulando un chat mientras el navegador navega a la URL
+                 if(!closedModal && window.location.pathname.match(/^\/inbox\/.+/)) {
-                     chatViewer.innerHTML = `
+                     const urlParams = new URLSearchParams(window.location.search);
-                
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] what-changed in inbox.html — confirmed 5x**: -             --bg-main: #1b2b4e;             
+             --bg-main: #213668;             

📌 IDE AST Context: Modified symbols likely include [html]
