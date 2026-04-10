import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        // Manejar subida de archivos (cámara/galería)
        window.uploadAdminMedia = async function(inputElem, wa_id) {"""

end_target = r"""        window.enviarMensajeManual = async function (e, wa_id) {"""

# I will use a regex to delete everything from window.uploadAdminMedia up to window.enviarMensajeManual
idx1 = text.find(target)
idx2 = text.find(end_target)
if idx1 != -1 and idx2 != -1:
    text = text[:idx1] + end_target + text[idx2 + len(end_target):]
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Cleaned inbox.html from redundant JS")
else:
    print("Could not find targets in inbox")

# Now let's fix server.py
with open("server.py", "r", encoding="utf-8") as f:
    server_text = f.read()

target_dropdown = r"""                <!-- Dropdown de Adjuntos -->
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
                
if target_dropdown in server_text:
    server_text = server_text.replace(target_dropdown, '                <input type="text" id="manualMsgInput" ')
    print("Removed duplicate dropdown from server.py")

target_menu = r"""                    <!-- Menú Flotante de Adjuntos -->
                    <div id="attachMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); left:0; width:190px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').click();" """

replacement_menu = r"""                    <!-- Menú Flotante de Adjuntos -->
                    <div id="attachMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); left:0; width:190px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').setAttribute('capture', 'environment'); document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg> Tomar Foto (Cámara)
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').removeAttribute('capture'); document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').click();" """

if target_menu in server_text:
    server_text = server_text.replace(target_menu, replacement_menu)
    print("Added Camera option to Attach Menu!")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(server_text)
