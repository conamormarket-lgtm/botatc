import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

toggle_script = """        // Alternar boton enviar / grabar audio
        window.toggleSendMicButton = function() {
            const input = document.getElementById('manualMsgInput');
            const submitMenu = document.getElementById('btnSubmitForm');
            const micMenu = document.getElementById('btnRecordAudio');
            if (input && submitMenu && micMenu) {
                if (input.value.trim().length > 0) {
                    submitMenu.style.display = 'flex';
                    micMenu.style.display = 'none';
                } else {
                    submitMenu.style.display = 'none';
                    micMenu.style.display = 'flex';
                }
            }
        };

        // Escuchar input manual
        document.addEventListener('input', function(e) {
            if(e.target.id === 'manualMsgInput') {
                window.toggleSendMicButton();
            }
        });
        
        """

if "window.toggleSendMicButton" not in text:
    idx = text.find('window.enviarMensajeManual = async function (e, wa_id) {')
    if idx != -1:
        text = text[:idx] + toggle_script + text[idx:]
        with open("inbox.html", "w", encoding="utf-8") as f:
            f.write(text)
        print("Injected toggleSendMicButton")
    else:
        print("Function toggleSendMicButton insertion point not found")
else:
    print("toggleSendMicButton already logic injected")
