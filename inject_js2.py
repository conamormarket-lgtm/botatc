import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        window.enviarMensajeManual = async function (e, wa_id) {"""

injection = r"""
        // Manejar subida de archivos (cámara/galería)
        window.uploadAdminMedia = async function(inputElem, wa_id) {
            if (!inputElem.files || inputElem.files.length === 0) return;
            
            const file = inputElem.files[0];
            if(!confirm(`¿Estás seguro de enviar el archivo "${file.name}" al cliente?`)) {
                inputElem.value = "";
                return;
            }
            
            const formData = new FormData();
            formData.append('wa_id', wa_id);
            formData.append('file', file);
            
            const btnAttach = document.getElementById('btnAttachMedia');
            const oldContent = btnAttach.innerHTML;
            btnAttach.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>';
            btnAttach.style.animation = 'spin 1s linear infinite';
            btnAttach.disabled = true;

            try {
                const res = await fetch('/api/admin/enviar_media_manual', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if(!data.ok){
                    alert("Error al enviar archivo: " + (data.error || "Desconocido"));
                } else {
                    // Forzar refresh PJAX del chat viewer
                    if (window.fetchInbox) window.fetchInbox();
                    else location.reload();
                }
            } catch (e) {
                alert("Error de subida: " + e.message);
            } finally {
                btnAttach.innerHTML = oldContent;
                btnAttach.style.animation = '';
                btnAttach.disabled = false;
                inputElem.value = "";
            }
        };

        // Agregar soporte para Pegar (Paste) en el input preventivo
        document.addEventListener('paste', async function(e) {
            const input = document.getElementById('manualMsgInput');
            if (!input || document.activeElement !== input) return;
            
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let index in items) {
                const item = items[index];
                if (item.kind === 'file') {
                    const blob = item.getAsFile();
                    
                    const urlParams = new URLSearchParams(window.location.search);
                    const wa_id = urlParams.get('wa_id');
                    if(!wa_id) return;
                    
                    if (confirm(`¿Pegar y enviar imagen compartida al chat?`)) {
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(new File([blob], "imagen_pegada.png", {type: blob.type}));
                        
                        const fileInput = document.getElementById('adminMediaInput');
                        if (fileInput) {
                            fileInput.files = dataTransfer.files;
                            window.uploadAdminMedia(fileInput, wa_id);
                        }
                    }
                }
            }
        });

        // Añadir estilo CSS de spin si no existe
        if(!document.getElementById('spinStyle')) {
            const style = document.createElement('style');
            style.id = 'spinStyle';
            style.textContent = '@keyframes spin { 100% { transform: rotate(360deg); } }';
            document.head.appendChild(style);
        }

        window.enviarMensajeManual = async function (e, wa_id) {"""

if target in text:
    text = text.replace(target, injection)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected logic correctly")
else:
    print("Target NOT FOUND in `inbox.html`!!")
