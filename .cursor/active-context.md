> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `inbox.html` (Domain: **Generic Logic**)

### 🔴 Generic Logic Gotchas
- **⚠️ GOTCHA: Fixed null crash in Aislar — reduces excessive function call frequency**: -                     const cleanHTML = (html) => html.replace(/style="[^"]*"/g, "").replace(/>\d+:\d{2}</g, ">0:00<");
+                     // Aislar temporalmente elementos de subida asíncrona (fantasmas)
-                     
+                     const tempNodes = Array.from(oldScroll.querySelectorAll('[data-temp="true"]'));
-                     const newChildren = Array.from(newScroll.children);
+                     tempNodes.forEach(node => oldScroll.removeChild(node));
-                     for (let i = 0; i < newChildren.length; i++) {
+                     const cleanHTML = (html) => html.replace(/style="[^"]*"/g, "").replace(/>\d+:\d{2}</g, ">0:00<");
-                         const newNode = newChildren[i];
+                     
-                         const oldNode = oldScroll.children[i];
+                     const newChildren = Array.from(newScroll.children);
-                         
+                     
-                         if (!oldNode) {
+                     for (let i = 0; i < newChildren.length; i++) {
-                             oldScroll.appendChild(newNode.cloneNode(true));
+                         const newNode = newChildren[i];
-                             didAppend = true;
+                         const oldNode = oldScroll.children[i];
-                         } else {
+                         
-                             if (cleanHTML(oldNode.innerHTML) !== cleanHTML(newNode.innerHTML)) {
+                         if (!oldNode) {
-                                 const audio = oldNode.querySelector('audio');
+                             oldScroll.appendChild(newNode.cloneNode(true));
-                                 if (audio && window._currentAudio === audio && !audio.paused) {
+                             didAppend = true;
-                                     continue;
+                         } else {
-                                 }
+                             if (clean
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **⚠️ GOTCHA: Fixed null crash in Botones — parallelizes async operations for speed**: -     # Inyectar CSS dinámico exacto al de inbox
+ 
-     custom_theme_css = ""
+     
-     c_bg = prefs.get('bg_main', '#0f172a')
+     # Botones Admin
-     c_prim = prefs.get('primary_color', '#3b82f6')
+     if es_admin(request):
-     c_acc = prefs.get('accent_bg', '#1e293b')
+         admin_btn = """<a href="/admin" class="nav-item" title="Panel Estadístico"><svg viewBox="0 0 24 24"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg></a>"""
-     c_acc_hex = c_acc.lstrip('#')
+         settings_btn = """<a href="/settings" class="nav-item" title="Personalizar Agente IA"><svg viewBox="0 0 24 24"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg></a>"""
-     if len(c_acc_hex) == 6:
+     else:
-         c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
+         admin_btn = ""
-         accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
+         settings_btn = ""
-         accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"
+         
-         accent_hover_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.08)"
+     html = html.replace("{admin_button}", admin_btn)
-     else:
+     html = html.replace("{settings_button}", settings_btn)
-         accent_bg_rgba = "rgba(255, 255, 255, 0.05)"
+ 
-         accent_border_rgba = "rgba(255, 255, 255, 0.1)"
+     return HTMLResponse(inyectar_tema_global(request, html))
-         accent_hover_rgba = "rgba(255, 255, 255, 0.08)"
+ 
-         
+ @app.get("/settings", response_class=HTMLResponse)
-     custom_theme_css = f'''
+ async def settings_panel(request: Request):
-         :root {{
+     """Personalización de Agente y Base de Conocimiento."""
-             --bg-main: {c_bg} !important;
+     if not es_admin(request):
-             --bg-sidebar: {c_bg} !important;
+      
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, startup_event, sesiones]

### 📐 Generic Logic Conventions & Fixes
- **[problem-fix] Fixed null crash in Falla — reduces excessive function call frequency**: -                     } else {
+                         setTimeout(() => { if (loadingBubble && loadingBubble.parentNode) loadingBubble.parentNode.removeChild(loadingBubble); }, 6000);
-                         showGlobalToast(`❌ Falla al enviar ${modeIcon} a +${wa_id}: ${data.error || "Desconocido"}`);
+                     } else {
-                     }
+                         showGlobalToast(`❌ Falla al enviar ${modeIcon} a +${wa_id}: ${data.error || "Desconocido"}`);
-                 }
+                     }
-             } catch (e) {
+                 }
-                 if (loadingBubble && document.body.contains(loadingBubble)) {
+             } catch (e) {
-                     loadingBubble.innerHTML = `❌ Falló la conexión de fondo.`;
+                 if (loadingBubble && document.body.contains(loadingBubble)) {
-                 } else {
+                     loadingBubble.innerHTML = `❌ Falló la conexión de fondo.`;
-                     showGlobalToast(`❌ Falló la subida de ${modeIcon} a +${wa_id} por error de red.`);
+                     loadingBubble.style.border = "1px solid red";
-                 }
+                     setTimeout(() => { if (loadingBubble && loadingBubble.parentNode) loadingBubble.parentNode.removeChild(loadingBubble); }, 6000);
-             }
+                 } else {
-         };
+                     showGlobalToast(`❌ Falló la subida de ${modeIcon} a +${wa_id} por error de red.`);
- 
+                 }
-         // NOTIFICACIONES GLOBALES INDESTRUCTIBLES
+             }
-         window.showGlobalToast = function(msg) {
+         };
-             const toast = document.createElement('div');
+ 
-             toast.style.position = 'fixed';
+         // NOTIFICACIONES GLOBALES INDESTRUCTIBLES
-             toast.style.bottom = '20px';
+         window.showGlobalToast = function(msg) {
-             toast.style.left = '50%';
+             const toast = document.createElement('div')
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Configuraci — reduces excessive function call frequency — confirmed 3x**: -         <!-- Logout Button (reemplazando al dot) -->
+         <!-- Configuración de Perfil Usuario -->
-         <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-top: auto; margin-bottom: 20px; color: #ef4444; display: flex; justify-content: center; text-decoration: none;">
+         <a href="/perfil" class="nav-item" title="Mi Perfil" style="margin-top: auto; margin-bottom: 5px; color: var(--text-muted); display: flex; justify-content: center; text-decoration: none;">
-             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 28px; height: 28px; opacity: 0.8; transition: opacity 0.2s;">
+             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 24px; height: 24px;">
-                 <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
+                 <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
-                 <polyline points="16 17 21 12 16 7"></polyline>
+                 <circle cx="12" cy="7" r="4"></circle>
-                 <line x1="21" y1="12" x2="9" y2="12"></line>
+             </svg>
-             </svg>
+         </a>
-         </a>
+         
- 
+         <!-- Logout Button (reemplazando al dot) -->
-     </nav>
+         <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-bottom: 20px; color: #ef4444; display: flex; justify-content: center; text-decoration: none;">
- 
+             <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 26px; height: 26px; opacity: 0.8; transition: opacity 0.2s;">
-     <!-- 2. PANEL CENTRAL (Lista de Chats) -->
+                 <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
-     <div class="chat-list-panel">
+                 <polyline points="16 17 2
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Video — reduces excessive function call frequency — confirmed 4x**: -                     if (loadingBubble) {
+                     if (loadingBubble && document.body.contains(loadingBubble)) {
-                     }
+                     } else {
-                 } else {
+                         showGlobalToast(`✅ ${modeIcon} ¡Video subido y enviado a +${wa_id} correctamente!`);
-                     if (loadingBubble && document.body.contains(loadingBubble)) {
+                     }
-                         loadingBubble.innerHTML = `❌ Error subiendo: ${data.error || "Desconocido"}`;
+                 } else {
-                         loadingBubble.style.border = "1px solid red";
+                     if (loadingBubble && document.body.contains(loadingBubble)) {
-                     } else {
+                         loadingBubble.innerHTML = `❌ Error subiendo: ${data.error || "Desconocido"}`;
-                         showGlobalToast(`❌ Falla al enviar ${modeIcon} a +${wa_id}: ${data.error || "Desconocido"}`);
+                         loadingBubble.style.border = "1px solid red";
-                     }
+                     } else {
-                 }
+                         showGlobalToast(`❌ Falla al enviar ${modeIcon} a +${wa_id}: ${data.error || "Desconocido"}`);
-             } catch (e) {
+                     }
-                 if (loadingBubble && document.body.contains(loadingBubble)) {
+                 }
-                     loadingBubble.innerHTML = `❌ Falló la conexión de fondo.`;
+             } catch (e) {
-                 } else {
+                 if (loadingBubble && document.body.contains(loadingBubble)) {
-                     showGlobalToast(`❌ Falló la subida de ${modeIcon} a +${wa_id} por error de red.`);
+                     loadingBubble.innerHTML = `❌ Falló la conexión de fondo.`;
-                 }
+                 } else {
-             }
+                     showGlobalToast(`❌ Falló la subida de ${modeIcon} a +${wa_id} por error de red.`);
-      
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Nivel — reduces excessive function call frequency — confirmed 4x**: -         .bubble-user .chat-phone { color: var(--primary-color) !important; text-decoration: underline; font-weight: bold; }
+         @keyframes spin { 100% { transform: rotate(360deg); } }
-         .bubble-bot .chat-phone { color: #ffffff !important; text-decoration: underline; font-weight: bold; }
+         .spin-anim { animation: spin 1s linear infinite; }
-         * { box-sizing: border-box; }
+         .bubble-user .chat-phone { color: var(--primary-color) !important; text-decoration: underline; font-weight: bold; }
-         body { overflow-x: hidden; max-width: 100vw; }
+         .bubble-bot .chat-phone { color: #ffffff !important; text-decoration: underline; font-weight: bold; }
-                 :root {
+         * { box-sizing: border-box; }
-             /* 1. Nivel de Color Principal */
+         body { overflow-x: hidden; max-width: 100vw; }
-             --primary-color: #3b82f6;       
+                 :root {
-             --primary-hover: #2563eb;       
+             /* 1. Nivel de Color Principal */
-             /* 2. Nivel de Color de Acento (translúcidos adaptables) */
+             --primary-color: #3b82f6;       
-             --accent-bg: rgba(255, 255, 255, 0.05);           
+             --primary-hover: #2563eb;       
-             --accent-border: rgba(255, 255, 255, 0.1);       
+             /* 2. Nivel de Color de Acento (translúcidos adaptables) */
-             --accent-hover-soft: rgba(255, 255, 255, 0.08);   
+             --accent-bg: rgba(255, 255, 255, 0.05);           
-             /* 3. Nivel de Color de Fondo General */
+             --accent-border: rgba(255, 255, 255, 0.1);       
-             --bg-main: #213668;             
+             --accent-hover-soft: rgba(255, 255, 255, 0.08);   
-             --bg-sidebar: var(--bg-main);
+             /* 3. Nivel de Color de Fondo General */
-             --bg-list: var(--bg-main);
+             --bg-main: #213668;             
-         
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[convention] Fixed null crash in Cargar — wraps unsafe operation in error boundary — confirmed 3x**: -                     alert("✅ Plantilla enviada. La ventana de 24 horas se debería abrir si el cliente responde.");
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
- **[what-changed] Updated schema FormData**: -             previewTheme();
+             
-             
+             // clear file input
-             const form = document.getElementById('themeForm');
+             document.querySelector('input[name="wallpaper_file"]').value = '';
-             const data = new FormData(form);
+             document.getElementById('localFileLabel').style.display = 'none';
-             await fetch("/api/user/theme", { method: "POST", body: data });
+             document.getElementById('localFileName').innerText = '';
-             window.location.reload();
+ 
-         }
+             previewTheme();
- 
+             
-         async function saveTheme(e) {
+             const form = document.getElementById('themeForm');
-             e.preventDefault();
+             const data = new FormData(form);
-             const form = document.getElementById('themeForm');
+             await fetch("/api/user/theme", { method: "POST", body: data });
-             const data = new FormData(form);
+             window.location.reload();
-             
+         }
-             const btn = form.querySelector('button');
+ 
-             const originalText = btn.innerText;
+         async function saveTheme(e) {
-             btn.innerText = "Guardando...";
+             e.preventDefault();
-             
+             const form = document.getElementById('themeForm');
-             try {
+             const data = new FormData(form);
-                 const res = await fetch("/api/user/theme", { method: "POST", body: data });
+             
-                 if(res.ok) {
+             const btn = form.querySelector('button');
-                     const statusText = document.getElementById("themeStatus");
+             const originalText = btn.innerText;
-                     statusText.style.display = "block";
+             btn.innerText = "Guardando...";
-                     setTimeout(() => statusText.style.display = "none", 4000);
+             
-                 } else {
+       
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Clear**: -         function previewTheme() {
+         function previewLocalWallpaper(input) {
-             const bgMain = document.getElementById('theme_bg_main').value;
+             if (input.files && input.files[0]) {
-             const primaryColor = document.getElementById('theme_primary_color').value;
+                 const label = document.getElementById('localFileLabel');
-             const accentBg = document.getElementById('theme_accent_bg').value;
+                 const name = document.getElementById('localFileName');
-             
+                 name.innerText = input.files[0].name;
-             document.documentElement.style.setProperty('--bg-main', bgMain);
+                 label.style.display = 'block';
-             document.documentElement.style.setProperty('--primary-color', primaryColor);
+                 
-             document.documentElement.style.setProperty('--accent-bg', accentBg);
+                 // Clear the URL input to avoid confusion
-         }
+                 document.getElementById('theme_wallpaper').value = '';
- 
+             }
-         async function restoreDefaultTheme() {
+         }
-             if(!confirm("¿Regresar a los colores originales?")) return;
+ 
-             document.getElementById('theme_bg_main').value = '#0f172a';
+         function previewTheme() {
-             document.getElementById('theme_primary_color').value = '#3b82f6';
+             const bgMain = document.getElementById('theme_bg_main').value;
-             document.getElementById('theme_accent_bg').value = '#1e293b';
+             const primaryColor = document.getElementById('theme_primary_color').value;
-             document.getElementById('theme_wallpaper').value = '';
+             const accentBg = document.getElementById('theme_accent_bg').value;
-             document.getElementById('theme_wallpaper_opacity').value = '0.15';
+             
-             document.getElementById('opacityVal').innerText = '0.15';
+             document.d
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[problem-fix] Fixed null crash in Sino — protects against XSS and CSRF token theft**: - 
+     wp_opacity = float(prefs.get('wallpaper_opacity', '0.15'))
-     c_acc_hex = c_acc.lstrip('#')
+ 
-     if len(c_acc_hex) == 6:
+     c_acc_hex = c_acc.lstrip('#')
-         c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
+     if len(c_acc_hex) == 6:
-         accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
+         c_acc_rgb = tuple(int(c_acc_hex[i:i+2], 16) for i in (0, 2, 4))
-         accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"
+         accent_bg_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.05)"
-         accent_hover_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.08)"
+         accent_border_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.1)"
-     else:
+         accent_hover_rgba = f"rgba({c_acc_rgb[0]}, {c_acc_rgb[1]}, {c_acc_rgb[2]}, 0.08)"
-         accent_bg_rgba = "rgba(255, 255, 255, 0.05)"
+     else:
-         accent_border_rgba = "rgba(255, 255, 255, 0.1)"
+         accent_bg_rgba = "rgba(255, 255, 255, 0.05)"
-         accent_hover_rgba = "rgba(255, 255, 255, 0.08)"
+         accent_border_rgba = "rgba(255, 255, 255, 0.1)"
- 
+         accent_hover_rgba = "rgba(255, 255, 255, 0.08)"
-     css = f'''
+ 
-         :root {{
+     css = f'''
-             --bg-main: {c_bg} !important;
+         :root {{
-             --bg-sidebar: {c_bg} !important;
+             --bg-main: {c_bg} !important;
-             --bg-list: {c_bg} !important;
+             --bg-sidebar: {c_bg} !important;
-             --primary-color: {c_prim} !important;
+             --bg-list: {c_bg} !important;
-             --accent-bg: {accent_bg_rgba} !important;
+             --primary-color: {c_prim} !important;
-             --accent-border: {accent_border_rgba} !important;
+             --accent-bg: {accent_bg_rgba} !important;
-             --accent-hover-soft: {accent_hover_rgba} !important;
+
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [app, inyectar_tema_global, custom_exception_handler, gemini_client, startup_event]
- **[what-changed] Updated schema FormData**: -             previewTheme();
+             document.getElementById('theme_wallpaper_opacity').value = '0.15';
-             
+             document.getElementById('opacityVal').innerText = '0.15';
-             const form = document.getElementById('themeForm');
+             previewTheme();
-             const data = new FormData(form);
+             
-             await fetch("/api/user/theme", { method: "POST", body: data });
+             const form = document.getElementById('themeForm');
-             window.location.reload();
+             const data = new FormData(form);
-         }
+             await fetch("/api/user/theme", { method: "POST", body: data });
- 
+             window.location.reload();
-         async function saveTheme(e) {
+         }
-             e.preventDefault();
+ 
-             const form = document.getElementById('themeForm');
+         async function saveTheme(e) {
-             const data = new FormData(form);
+             e.preventDefault();
-             
+             const form = document.getElementById('themeForm');
-             const btn = form.querySelector('button');
+             const data = new FormData(form);
-             const originalText = btn.innerText;
+             
-             btn.innerText = "Guardando...";
+             const btn = form.querySelector('button');
-             
+             const originalText = btn.innerText;
-             try {
+             btn.innerText = "Guardando...";
-                 const res = await fetch("/api/user/theme", { method: "POST", body: data });
+             
-                 if(res.ok) {
+             try {
-                     const statusText = document.getElementById("themeStatus");
+                 const res = await fetch("/api/user/theme", { method: "POST", body: data });
-                     statusText.style.display = "block";
+                 if(res.ok) {
-                     setTimeout(() => statusText.style.display = "none", 4000);
+                    
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [html]
- **[what-changed] Updated schema Theme**: -     </script>
+ 
- </body>
+         // --- Theme Personalization Logic ---
- 
+         function previewTheme() {
- </html>
+             const bgMain = document.getElementById('theme_bg_main').value;
+             const primaryColor = document.getElementById('theme_primary_color').value;
+             const accentBg = document.getElementById('theme_accent_bg').value;
+             
+             document.documentElement.style.setProperty('--bg-main', bgMain);
+             document.documentElement.style.setProperty('--primary-color', primaryColor);
+             
+             // Minimal rgba handling for preview
+             document.documentElement.style.setProperty('--accent-bg', accentBg);
+         }
+ 
+         async function saveTheme(e) {
+             e.preventDefault();
+             const form = document.getElementById('themeForm');
+             const data = new FormData(form);
+             
+             const btn = form.querySelector('button');
+             const originalText = btn.innerText;
+             btn.innerText = "Guardando...";
+             
+             try {
+                 const res = await fetch("/api/user/theme", {
+                     method: "POST",
+                     body: data
+                 });
+                 if(res.ok) {
+                     const statusText = document.getElementById("themeStatus");
+                     statusText.style.display = "block";
+                     setTimeout(() => statusText.style.display = "none", 4000);
+                 } else {
+                     alert("Error servidor");
+                 }
+             } catch(e) {
+                 alert("Error cliente");
+             } finally {
+                 btn.innerText = originalText;
+             }
+         }
+     </script>
+ </body>
+ 
+ </html>

📌 IDE AST Context: Modified symbols likely include [html]
