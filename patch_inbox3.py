# -*- coding: utf-8 -*-
import sys

def patch():
    with open('inbox.html', 'r', encoding='utf-8') as f:
        html = f.read()

    css_code = '''
    .media-queue-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 10px;
        background: var(--bg-main);
        border-bottom: 1px solid var(--accent-border);
        max-height: 150px;
        overflow-y: auto;
    }
    .media-queue-item {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        background-size: cover;
        background-position: center;
        position: relative;
        border: 1px solid var(--accent-border);
    }
    .media-queue-loading {
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 0.8rem;
        border-radius: 8px;
    }
    .media-queue-remove {
        position: absolute;
        top: -5px;
        right: -5px;
        background: var(--danger-color);
        color: white;
        border-radius: 50%;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 12px;
        border: none;
    }
</style>'''

    if '.media-queue-container' not in html:
        html = html.replace('</style>', css_code)

    queue_ui = '''        window.pendingUploads = [];
        
        window.renderPendingMediaUI = function() {
            let qContainer = document.getElementById('pendingMediaQueue');
            if (!qContainer) {
                qContainer = document.createElement('div');
                qContainer.id = 'pendingMediaQueue';
                qContainer.className = 'media-queue-container';
                const chatInputWrap = document.querySelector('.chat-input-wrapper');
                chatInputWrap.parentNode.insertBefore(qContainer, chatInputWrap);
            }
            
            if (window.pendingUploads.length === 0) {
                qContainer.style.display = 'none';
                return;
            }
            
            qContainer.style.display = 'flex';
            qContainer.innerHTML = '';
            window.pendingUploads.forEach((up, idx) => {
                const el = document.createElement('div');
                el.className = 'media-queue-item';
                
                if (up.file && up.file.type.startsWith('image/')) {
                    el.style.backgroundImage = url();
                } else {
                    el.style.background = '#333';
                    el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-size:24px;">\U0001F4C4</div>';
                }
                
                if (idx === 0) {
                    const badge = document.createElement('div');
                    badge.innerText = 'Texto';
                    badge.style.position = 'absolute';
                    badge.style.bottom = '2px';
                    badge.style.left = '2px';
                    badge.style.fontSize = '10px';
                    badge.style.background = 'var(--primary-color)';
                    badge.style.color = 'white';
                    badge.style.padding = '0px 4px';
                    badge.style.borderRadius = '3px';
                    el.appendChild(badge);
                }

                if (up.error) {
                    el.style.border = '2px solid red';
                } else if (!up.media_id) {
                    const ld = document.createElement('div');
                    ld.className = 'media-queue-loading';
                    ld.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-anim"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>';
                    el.appendChild(ld);
                }

                const rm = document.createElement('button');
                rm.className = 'media-queue-remove';
                rm.innerHTML = 'X';
                rm.onclick = () => {
                    window.pendingUploads.splice(idx, 1);
                    window.renderPendingMediaUI();
                };
                el.appendChild(rm);
                
                qContainer.appendChild(el);
            });
        };

        window.enviarMensajeManual = async function (e, wa_id) {'''

    if 'window.pendingUploads = [];' not in html:
        html = html.replace('        window.enviarMensajeManual = async function (e, wa_id) {', queue_ui)

    # Re-write enviarMensajeManual block completely (find start index, find end index)
    start_idx = html.find('        window.enviarMensajeManual = async function (e, wa_id) {')
    end_idx = html.find('        // LIBRERÍA LOCAL DE STICKERS')
    if end_idx == -1: end_idx = html.find('        // LIBRER\xcdA LOCAL DE STICKERS')
    if end_idx == -1: end_idx = html.find('cargarStickers = async function () {')
    if end_idx != -1 and start_idx != -1:
        # Move end_idx backwards to the start of "window.cargarStickers"
        end_idx = html.rfind('        // LIBRER', start_idx, end_idx+50)

    if start_idx != -1 and end_idx != -1:
        new_enviar_block = '''        window.enviarMensajeManual = async function (e, wa_id) {
            e.preventDefault();
            const input = document.getElementById('manualMsgInput');
            if (!input) return;
            const msj = input.value.trim();
            const hasPendingUploads = window.pendingUploads && window.pendingUploads.length > 0;
            
            if (!msj && !hasPendingUploads) return;

            const replyWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;

            if (hasPendingUploads) {
                // Wait for all uploads to complete (have media_id) or error
                const inProgress = window.pendingUploads.filter(u => !u.media_id && !u.error);
                if (inProgress.length > 0) {
                    alert("Aún hay archivos subiéndose, por favor espera un instante y vuelve a presionar enviar.");
                    return;
                }
                
                const validUploads = window.pendingUploads.filter(u => u.media_id);
                if (validUploads.length === 0) {
                    alert("No se pudo subir ningún archivo válido.");
                    window.pendingUploads = [];
                    window.renderPendingMediaUI();
                    return;
                }

                // Process first upload with caption
                const firstUp = validUploads[0];
                let encCaption = msj ? "|caption:" + encodeURIComponent(msj) : "";
                let firstMsgText = [:];
                
                // Process subsequent uploads without caption
                let remainingMessages = [];
                for (let i = 1; i < validUploads.length; i++) {
                    remainingMessages.push([:]);
                }

                // Clean the UI HTML first
                input.value = '';
                input.focus();
                window.pendingUploads = [];
                window.renderPendingMediaUI();
                if (document.getElementById('replyPreviewContainer')) {
                    document.getElementById('replyPreviewContainer').style.display = 'none';
                    if (document.getElementById('replyToWamid')) document.getElementById('replyToWamid').value = '';
                }

                // Send first message
                await window._sendRawTextManual(firstMsgText, wa_id, msj || "[Archivos enviados]", replyWamid);

                // Send remaining messages sequentially
                for (let rMsg of remainingMessages) {
                    await window._sendRawTextManual(rMsg, wa_id, "", null);
                }
                setTimeout(() => window.location.reload(), 500);
                return;
            }

            // Normal text
            input.value = '';
            input.focus();
            if (document.getElementById('replyPreviewContainer')) {
                document.getElementById('replyPreviewContainer').style.display = 'none';
                if (document.getElementById('replyToWamid')) document.getElementById('replyToWamid').value = '';
            }
            await window._sendRawTextManual(msj, wa_id, msj, replyWamid);
        };

        window._sendRawTextManual = async function(rawPayload, wa_id, optimisticText, replyWamid) {
            const scroll = document.getElementById('chatScroll');
            let bubble = null;
            if (scroll && optimisticText) {
                bubble = document.createElement('div');
                bubble.className = "bubble bubble-bot lado-der";
                bubble.style.border = "1px solid var(--primary-color)";
                bubble.innerText = optimisticText;
                scroll.appendChild(bubble);
                scroll.scrollTop = scroll.scrollHeight;
            }
            try {
                const qrTitleToPass = window._nextQuickReplyTitle || null;
                window._nextQuickReplyTitle = null;
                
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: rawPayload, reply_to_wamid: replyWamid, quick_reply_title: qrTitleToPass })
                });

                const data = await res.json();
                if (!data.ok) {
                    if (scroll && bubble) scroll.removeChild(bubble);
                    if (data.error === "META_API_REJECTED") {
                        alert("Error de WhatsApp (Meta): No puedes enviar mensajes libres a este número.");
                    } else {
                        alert("Error no controlado al enviar: " + data.error);
                    }
                }
            } catch (e) {
                console.error("Fallo al enviar:", e);
                if (scroll && bubble) scroll.removeChild(bubble);
                alert("Error de red conectando con el panel Web o timeout.");
            }
        };
'''
        if '_sendRawTextManual' not in html[start_idx:end_idx]:
            html = html[:start_idx] + new_enviar_block + html[end_idx:]


    # REWRITE uploadMedia
    st2 = html.find("const uploadMedia = async (file, mode = 'imagen') => {")
    e2 = html.find('        document.getElementById(\'stickersGrid\')', st2)
    if e2 == -1: e2 = html.find("document.addEventListener('dragover', function(e) {", st2)
    if e2 == -1: e2 = html.find("        // Trigger de los inputs", st2)
    
    if st2 != -1 and e2 != -1:
        # We need to find the correct end of uploadMedia. It ends with "};". Let's rfind from e2.
        eol = html.rfind('};', st2, e2)
        if eol != -1: e2 = eol + 2
        
        new_upload_media = '''const uploadMedia = async (file, mode = 'imagen') => {
            const wa_id = window.location.pathname.split('/').pop();
            if (!wa_id || isNaN(wa_id) || wa_id === 'inbox') {
                alert("Debes tener un chat abierto para enviar multimedia directamente.");
                return;
            }

            const upObj = { file, mode, media_id: null, error: null };
            window.pendingUploads.push(upObj);
            window.renderPendingMediaUI();

            const compressImage = async (inputFile) => {
                if (!inputFile.type.startsWith('image/') || inputFile.type === 'image/gif' || inputFile.size < 2.5 * 1024 * 1024) return inputFile;
                return new Promise((resolve) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        let w = img.width, h = img.height;
                        const maxDim = 1920; 
                        if (w > h && w > maxDim) { h *= maxDim / w; w = maxDim; }
                        else if (h > maxDim) { w *= maxDim / h; h = maxDim; }
                        canvas.width = w; canvas.height = h;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, w, h);
                        canvas.toBlob((b) => resolve(new File([b], inputFile.name || "foto_opt.jpg", { type: "image/jpeg" })), "image/jpeg", 0.80);
                    };
                    img.onerror = () => resolve(inputFile);
                    img.src = URL.createObjectURL(inputFile);
                });
            };

            if (mode === 'imagen') {
                file = await compressImage(file);
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("mode", mode);

            try {
                const uploadRes = await fetch('/api/admin/upload_media', {
                    method: 'POST',
                    body: formData
                });

                const uploadData = await uploadRes.json();
                if (!uploadData.ok) {
                    upObj.error = uploadData.error || 'Error subiendo';
                    window.renderPendingMediaUI();
                    return;
                }

                upObj.media_id = uploadData.media_id;
                window.renderPendingMediaUI();

            } catch (e) {
                console.error("Fallo de red al enviar media:", e);
                upObj.error = "Error red";
                window.renderPendingMediaUI();
            }
        };'''
        if 'window.pendingUploads.push' not in html[st2:e2]:
            html = html[:st2] + new_upload_media + "\n" + html[e2:]

    # Add Drag and drop
    drop_events = '''
        document.addEventListener('dragover', function(e) {
            if (e.target && e.target.id === 'manualMsgInput') {
                e.preventDefault();
                e.stopPropagation();
                e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
            }
        });
        document.addEventListener('dragleave', function(e) {
            if (e.target && e.target.id === 'manualMsgInput') {
                e.preventDefault();
                e.stopPropagation();
                e.target.style.backgroundColor = 'transparent';
            }
        });
        document.addEventListener('drop', function(e) {
            if (e.target && e.target.id === 'manualMsgInput') {
                e.preventDefault();
                e.stopPropagation();
                e.target.style.backgroundColor = 'transparent';
                if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    Array.from(e.dataTransfer.files).forEach(file => {
                        let mode = 'documento';
                        if (file.type.startsWith('image/')) mode = 'imagen';
                        else if (file.type.startsWith('video/')) mode = 'video';
                        else if (file.type.startsWith('audio/')) mode = 'audio';
                        uploadMedia(file, mode);
                    });
                }
            }
        });
'''
    if "document.addEventListener('dragover" not in html:
        html = html.replace("        // Trigger de los inputs ocultos", drop_events + "\n        // Trigger de los inputs ocultos")

    # Update input loop for multiple files
    if "Array.from(e.target.files).forEach" not in html:
        old_change = "if (e.target.files && e.target.files[0]) {"
        new_change = '''if (e.target.files && e.target.files.length > 0) {
                    Array.from(e.target.files).forEach(file => {
                        let dynamicMode = reqMode;
                        if (reqMode === 'documento') {
                            if (file.type.startsWith('image/')) dynamicMode = 'imagen';
                            else if (file.type.startsWith('video/')) dynamicMode = 'video';
                            else if (file.type.startsWith('audio/')) dynamicMode = 'audio';
                        }
                        uploadMedia(file, dynamicMode);
                    });
                }'''
        html = html.replace(old_change + "\n                    uploadMedia(e.target.files[0], reqMode);\n                }", new_change)
        
        html = html.replace('<input type="file" id="hiddenFileInput" style="display:none;" accept="image/*">', '<input type="file" id="hiddenFileInput" style="display:none;" multiple accept="*/*">')

    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(html)

patch()
