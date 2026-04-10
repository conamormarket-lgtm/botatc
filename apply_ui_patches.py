import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Fix 1: height 100vh -> height 100dvh for better mobile sizing
if 'height: 100vh;' in text:
    text = text.replace('height: 100vh;', 'height: 100dvh;')

# Fix 2: -webkit-overflow-scrolling
if '#chatScroll {' not in text:
    target = r"""        .chat-burbuja {
            max-width: 75%;
            padding: 12px 16px;"""
    replacement = r"""        #chatScroll {
            -webkit-overflow-scrolling: touch;
        }
        .chat-burbuja {
            max-width: 75%;
            padding: 12px 16px;"""
    if target in text:
        text = text.replace(target, replacement)

# Fix 3: Media dropdown functionality JS
target_js = r"""        // Añadir estilo CSS de spin si no existe"""
replacement_js = r"""        // Funcionalidad de dropdown de clip
        window.toggleClipMenu = function() {
            const menu = document.getElementById('clipActionMenu');
            if(menu) {
                menu.style.display = menu.style.display === 'none' ? 'flex' : 'none';
            }
        };
        // Cerrar menú si clickea fuera
        document.addEventListener('click', function(e) {
            const btn = document.getElementById('btnAttachMediaDropdown');
            const menu = document.getElementById('clipActionMenu');
            if(btn && menu && !btn.contains(e.target) && !menu.contains(e.target)) {
                menu.style.display = 'none';
            }
        });

        // Añadir estilo CSS de spin si no existe"""
if target_js in text:
    text = text.replace(target_js, replacement_js)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

# ------------- Now patch SERVER.PY for the UI -------------

with open("server.py", "r", encoding="utf-8") as f:
    server_text = f.read()

target_server = r"""                <!-- Input oculto para subida de medios -->
                <input type="file" id="adminMediaInput" accept="image/*,video/*,audio/*,application/pdf" style="display:none;" onchange="uploadAdminMedia(this, '{wa_id}')">
                <button type="button" id="btnAttachMedia" onclick="document.getElementById('adminMediaInput').click();" style="background:none; border:none; color:var(--text-muted); cursor:pointer; padding:10px; display:flex; align-items:center; transition:color 0.2s;" title="Adjuntar (Foto, Video, Doc)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                </button>
                <input type="text" id="manualMsgInput" """

replacement_server = r"""                <!-- Dropdown de Adjuntos -->
                <div style="position:relative;">
                    <button type="button" id="btnAttachMediaDropdown" onclick="toggleClipMenu()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; padding:10px; display:flex; align-items:center; transition:color 0.2s;" title="Opciones de Adjunto">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                    </button>
                    <!-- Menú emergente tipo WhatsApp Web -->
                    <div id="clipActionMenu" style="display:none; position:absolute; bottom:55px; left:0; background:var(--bg-sidebar); border:1px solid var(--accent-border); border-radius:16px; padding:12px; flex-direction:column; gap:15px; box-shadow:0 8px 30px rgba(0,0,0,0.3); z-index:999; min-width:60px; align-items:center;">
                        
                        <!-- Opción Cámara/Galería -->
                        <div style="display:flex; flex-direction:column; align-items:center; gap:8px; cursor:pointer;" onclick="document.getElementById('adminMediaInput').click(); toggleClipMenu();">
                            <div style="background: linear-gradient(135deg, #00B2FF, #006AFF); width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; box-shadow:0 4px 10px rgba(0,106,255,0.4); transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                            </div>
                            <span style="font-size:0.75rem; color:var(--text-main); font-weight:500;">Fotos</span>
                        </div>

                    </div>
                </div>
                <!-- Input oculto cámara/documento -->
                <input type="file" id="adminMediaInput" accept="image/*,video/*,audio/*,application/pdf" style="display:none;" onchange="uploadAdminMedia(this, '{wa_id}')">
                
                <input type="text" id="manualMsgInput" """

if target_server in server_text:
    server_text = server_text.replace(target_server, replacement_server)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(server_text)

print("UI patches applied!")
