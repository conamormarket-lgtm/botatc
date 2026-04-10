import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""                <input type="text" id="manualMsgInput" placeholder="Escribe un mensaje"""

replacement = r"""                <!-- Input oculto para subida de medios -->
                <input type="file" id="adminMediaInput" accept="image/*,video/*,audio/*,application/pdf" style="display:none;" onchange="uploadAdminMedia(this, '""" + r"""{wa_id}""" + r"""')">
                <button type="button" id="btnAttachMedia" onclick="document.getElementById('adminMediaInput').click();" style="background:none; border:none; color:var(--text-muted); cursor:pointer; padding:10px; display:flex; align-items:center; transition:color 0.2s;" title="Adjuntar (Foto, Video, Doc)">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                </button>
                <input type="text" id="manualMsgInput" placeholder="Escribe un mensaje"""

if target in text:
    text = text.replace(target, replacement)
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched server.py successfully!")
else:
    print("Target not found in server.py")

