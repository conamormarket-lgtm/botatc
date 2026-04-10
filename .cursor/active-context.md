> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Array — prevents null/undefined runtime crashes**: -                     if (oldScroll.innerHTML !== newScroll.innerHTML) {
+                     const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
-                         // Respetar scroll solo si el usuario no ha subido a leer
+                     let didAppend = false;
-                         const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
+                     
-                         oldScroll.innerHTML = newScroll.innerHTML;
+                     const cleanHTML = (html) => html.replace(/style="[^"]*"/g, "").replace(/>\d+:\d{2}</g, ">0:00<");
-                         if (isAtBottom) {
+                     
-                             oldScroll.scrollTop = oldScroll.scrollHeight;
+                     const newChildren = Array.from(newScroll.children);
-                         }
+                     
-                     }
+                     for (let i = 0; i < newChildren.length; i++) {
-                 }
+                         const newNode = newChildren[i];
-             } catch (e) {
+                         const oldNode = oldScroll.children[i];
-                 console.warn('Error en Live Chat Polling:', e);
+                         
-             }
+                         if (!oldNode) {
-         }, 1500);
+                             oldScroll.appendChild(newNode.cloneNode(true));
- 
+                             didAppend = true;
-         // API CLIENT PARA RESPONDER
+                         } else {
-         
+                             if (cleanHTML(oldNode.innerHTML) !== cleanHTML(newNode.innerHTML)) {
-         
+                                 const audio = oldNode.querySelector('audio');
-         // NATIVE AUDIO RECORDING LOGIC
+                                 if (audio && window._currentAudio === audio && !audio.paused) {
-         let mediaRecorder;
+                        
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **⚠️ GOTCHA: problem-fix in server.py**: -                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 100%; max-height: 400px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
+                     return f"""<div style="text-align:center; max-width: 350px; margin: 0 auto;"><img src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
-                     return f"""<div style="text-align:center;"><video controls src="{src_url}" style="width: 100%; max-width: 250px; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; box-sizing: border-box; display: block;"></video></div>"""
+                     return f"""<div style="text-align:center; max-width: 350px; margin: 0 auto;"><video controls src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; display: block; margin: 0 auto;"></video></div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: problem-fix in server.py**: -                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 100%; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
+                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 100%; max-height: 400px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **⚠️ GOTCHA: problem-fix in server.py**: -                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 250px; min-height: 100px; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: inline-block; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""
+                     return f"""<div style="text-align:center;"><img src="{src_url}" style="max-width: 100%; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>"""

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in Apply — reduces excessive function call frequency**: -             const savedScroll = sessionStorage.getItem('chatListScrollTop');
+             const applyScroll = () => {
-             if (savedScroll) {
+                 const s = sessionStorage.getItem('chatListScrollTop');
-                 setTimeout(() => { chatsContainerDiv.scrollTop = parseInt(savedScroll); }, 50);
+                 if (s) chatsContainerDiv.scrollTop = parseInt(s);
-             }
+             };
-             chatsContainerDiv.addEventListener('scroll', function() {
+             
-                 sessionStorage.setItem('chatListScrollTop', this.scrollTop);
+             // Apply immediately, and firmly a few times to beat browser rendering or filter passes
-             });
+             applyScroll();
-         }
+             setTimeout(applyScroll, 50);
- 
+             setTimeout(applyScroll, 150);
- 
+             setTimeout(applyScroll, 300);
-         function iniciarNuevoChat() {
+ 
-             let val = document.getElementById('chatSearchInput').value.trim();
+             // Record cleanly using event listener, throttled/debounced implicitly? 
-             val = val.replace(/\D/g, ''); // purgar caracteres no numéricos
+             chatsContainerDiv.addEventListener('scroll', function() {
-             if (val.length < 9) return alert("Número muy corto");
+                 sessionStorage.setItem('chatListScrollTop', this.scrollTop);
-             if (!val.startsWith("51")) val = "51" + val;
+             });
-             window.location.href = `/inbox/${val}`;
+ 
-         }
+             // Adicionalmente, asegurar que si se hace clic en un chat, se guarde justo ese instante
- 
+             const chatLinks = chatsContainerDiv.querySelectorAll('.chat-row');
-         // EMOJI PICKER HOOK - Global event delegation
+             chatLinks.forEach(link => {
-         document.addEventListener('emoji-click', event => {
+                 link.addEventListener('click', () => {
-          
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in EMOJI — wraps unsafe operation in error boundary — confirmed 3x**: - 
+         const chatsContainerDiv = document.getElementById('regularChatsContainer');
-         function iniciarNuevoChat() {
+         if (chatsContainerDiv) {
-             let val = document.getElementById('chatSearchInput').value.trim();
+             const savedScroll = sessionStorage.getItem('chatListScrollTop');
-             val = val.replace(/\D/g, ''); // purgar caracteres no numéricos
+             if (savedScroll) {
-             if (val.length < 9) return alert("Número muy corto");
+                 setTimeout(() => { chatsContainerDiv.scrollTop = parseInt(savedScroll); }, 50);
-             if (!val.startsWith("51")) val = "51" + val;
+             }
-             window.location.href = `/inbox/${val}`;
+             chatsContainerDiv.addEventListener('scroll', function() {
-         }
+                 sessionStorage.setItem('chatListScrollTop', this.scrollTop);
- 
+             });
-         // EMOJI PICKER HOOK - Global event delegation
+         }
-         document.addEventListener('emoji-click', event => {
+ 
-             const input = document.getElementById('manualMsgInput');
+ 
-             if (input) {
+         function iniciarNuevoChat() {
-                 input.value += event.detail.unicode;
+             let val = document.getElementById('chatSearchInput').value.trim();
-                 input.focus();
+             val = val.replace(/\D/g, ''); // purgar caracteres no numéricos
-             }
+             if (val.length < 9) return alert("Número muy corto");
-         });
+             if (!val.startsWith("51")) val = "51" + val;
- 
+             window.location.href = `/inbox/${val}`;
-         // CERRAR MENÚS FLOTANTES AL HACER CLICK AFUERA
+         }
-         document.addEventListener("click", function (e) {
+ 
-             const combinedEmojiMenu = document.getElementById("combinedEmojiMenu");
+         // EMOJI PICKER HOOK - Global event delegation
-             if (combinedEmojiM
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in CUSTOM — wraps unsafe operation in error boundary — confirmed 3x**: -         window.toggleSendMicButton = function() {
+         // CUSTOM AUDIO PLAYER LOGIC
-             if (window._isAudioRecording) return; // No alternar si estamos grabando
+         window.formatAudioTime = function(seconds) {
-             const input = document.getElementById('manualMsgInput');
+             if (!seconds || isNaN(seconds)) return "0:00";
-             const submitMenu = document.getElementById('btnSubmitForm');
+             const min = Math.floor(seconds / 60);
-             const micMenu = document.getElementById('btnRecordAudio');
+             const sec = Math.floor(seconds % 60);
-             if (input && submitMenu && micMenu) {
+             return min + ":" + (sec < 10 ? "0" : "") + sec;
-                 if (input.value.trim().length > 0) {
+         };
-                     submitMenu.style.display = 'flex';
+ 
-                     micMenu.style.display = 'none';
+         window._currentAudio = null;
-                 } else {
+         window._currentBtn = null;
-                     submitMenu.style.display = 'none';
+         window.toggleAudio = function(btn) {
-                     micMenu.style.display = 'flex';
+             const container = btn.closest('.custom-audio-player');
-                 }
+             const audio = container.querySelector('audio');
-             }
+             const iconPlay = btn.querySelector('.icon-play');
-         };
+             const iconPause = btn.querySelector('.icon-pause');
-         // Escuchar input manual
+             if (window._currentAudio && window._currentAudio !== audio) {
-         document.addEventListener('input', function(e) {
+                 window._currentAudio.pause();
-             if(e.target.id === 'manualMsgInput') {
+                 if (window._currentBtn) {
-                 window.toggleSendMicButton();
+                     window._currentBtn.querySelector('.icon-play').style.display = 'block';
-             }
+   
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[trade-off] trade-off in inbox.html**: -                 const m = document.getElementById('emojiMenu');
+                 const m = document.getElementById('combinedEmojiMenu');
-             const emojiMenu = document.getElementById("emojiMenu");
+             const combinedEmojiMenu = document.getElementById("combinedEmojiMenu");
-             if (emojiMenu && !e.target.closest('#emojiMenu') && !e.target.closest('button[title="Emojis"]')) {
+             if (combinedEmojiMenu && !e.target.closest('#combinedEmojiMenu') && !e.target.closest('button[title="Emojis y Stickers"]')) {
-                 emojiMenu.style.display = "none";
+                 combinedEmojiMenu.style.display = "none";

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in inbox.html**: -                     btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
+                     isRecording = false;
-                     btnRecord.style.color = "var(--text-main)";
+                     window._isAudioRecording = false;
-                 }
+                     if(window.toggleSendMicButton) window.toggleSendMicButton();
-                 btnCancel.style.display = 'none';
+                     btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
-             }
+                     btnRecord.style.color = "var(--text-main)";
-         });
+                 }
-     </script>
+                 btnCancel.style.display = 'none';
- </body>
+             }
- 
+         });
- </html>
+     </script>
+ </body>
+ 
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Alternar — wraps unsafe operation in error boundary — confirmed 4x**: -         window.enviarMensajeManual = async function (e, wa_id) {
+                 // Alternar boton enviar / grabar audio
-             e.preventDefault();
+         window.toggleSendMicButton = function() {
-             if (!input) return;
+             const submitMenu = document.getElementById('btnSubmitForm');
-             const msj = input.value.trim();
+             const micMenu = document.getElementById('btnRecordAudio');
-             if (!msj) return;
+             if (input && submitMenu && micMenu) {
- 
+                 if (input.value.trim().length > 0) {
-             // Vaciar y enfocar
+                     submitMenu.style.display = 'flex';
-             input.value = '';
+                     micMenu.style.display = 'none';
-             input.focus();
+                 } else {
- 
+                     submitMenu.style.display = 'none';
-             // Dibujado optimista instantáneo
+                     micMenu.style.display = 'flex';
-             const scroll = document.getElementById('chatScroll');
+                 }
-             if (scroll) {
+             }
-                 const bubble = document.createElement('div');
+         };
-                 bubble.className = "bubble bubble-bot lado-der";
+ 
-                 bubble.style.border = "1px solid var(--primary-color)";
+         // Escuchar input manual
-                 bubble.innerText = msj;
+         document.addEventListener('input', function(e) {
-                 scroll.appendChild(bubble);
+             if(e.target.id === 'manualMsgInput') {
-                 scroll.scrollTop = scroll.scrollHeight;
+                 window.toggleSendMicButton();
- 
+         });
-             const replyWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
+         
-             if (document.getElementById('replyPreviewContainer')) {
+         window.enviarMensajeManual = async function (e, wa
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] what-changed in check_chat.py**: - idx = s.find('<a href="/inbox/')
+ idx = s.find('lista_chats_html +=')
- print(s[max(0,idx-50):idx+500])
+ print(s[max(0,idx-50):idx+800])

📌 IDE AST Context: Modified symbols likely include [s, idx]
- **[what-changed] what-changed in check_chat.py**: - idx = s.find('class="chat-item')
+ idx = s.find('<a href="/inbox/')
- print(s[max(0,idx-50):idx+300])
+ print(s[max(0,idx-50):idx+500])

📌 IDE AST Context: Modified symbols likely include [s, idx]
- **[what-changed] Updated firebase_client database schema**: - class LabelPayload(BaseModel):
+ class InitChatPayload(BaseModel):
-     id: str
+     wa_id: str
-     name: Optional[str] = None
+ 
-     color: Optional[str] = None
+ @app.post("/api/admin/chat/init")
- 
+ async def api_init_chat(payload: InitChatPayload, request: Request):
- @app.post("/api/admin/labels/save")
+     if not verificar_sesion(request): raise HTTPException(status_code=403)
- async def api_save_label(payload: LabelPayload, request: Request):
+     num_norm = normalizar_numero(payload.wa_id)
-     if not verificar_sesion(request):
+     obtener_o_crear_sesion(num_norm)
-         raise HTTPException(status_code=403, detail="No autorizado")
+     return {"ok": True, "wa_id": num_norm}
-     from firebase_client import guardar_etiqueta_bd
+ 
-     guardar_etiqueta_bd(payload.id, payload.name, payload.color)
+ class LabelPayload(BaseModel):
-     global global_labels
+     id: str
-     global_labels = [l for l in global_labels if l.get("id") != payload.id]
+     name: Optional[str] = None
-     global_labels.append({"id": payload.id, "name": payload.name, "color": payload.color})
+     color: Optional[str] = None
-     return {"ok": True}
+ 
- 
+ @app.post("/api/admin/labels/save")
- @app.post("/api/admin/labels/delete")
+ async def api_save_label(payload: LabelPayload, request: Request):
- async def api_delete_label(payload: LabelPayload, request: Request):
+     if not verificar_sesion(request):
-     if not verificar_sesion(request):
+         raise HTTPException(status_code=403, detail="No autorizado")
-         raise HTTPException(status_code=403, detail="No autorizado")
+     from firebase_client import guardar_etiqueta_bd
-     from firebase_client import eliminar_etiqueta_bd
+     guardar_etiqueta_bd(payload.id, payload.name, payload.color)
-     eliminar_etiqueta_bd(payload.id)
+     global global_labels
-     global global_labels
+     global_labels = [l for l in global_labels if l.get("id") != pay
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[what-changed] what-changed in server.py**: -                 return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
+                 return f'<span class="chat-phone" style="text-decoration:underline; cursor:pointer; font-weight:bold;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
-                     return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
+                     return f'<span class="chat-phone" style="text-decoration:underline; cursor:pointer; font-weight:bold;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
- **[convention] what-changed in server.py — confirmed 3x**: -                     return f'<div style="text-align:center;"><audio controls src="{src_url}" style="width: 100%; max-width: 250px; height: 40px; outline: none; margin-bottom: 5px; box-sizing: border-box; display: block;"></audio></div>'
+                     return f'<div style="min-width: 250px; max-width: 100%; margin: 0 auto; display: flex;"><audio controls src="{src_url}" style="width: 100%; height: 45px; outline: none; margin-bottom: 5px; border-radius: 20px;"></audio></div>'

📌 IDE AST Context: Modified symbols likely include [app, gemini_client, startup_event, sesiones, global_labels]
