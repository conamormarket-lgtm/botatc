# -*- coding: utf-8 -*-
import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add queue CSS
css_to_add = '''
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
'''
if '.media-queue-container' not in html:
    html = html.replace('</style>', css_to_add + '</style>')


# Pending uploads variable
if 'window.pendingUploads =' not in html:
    html = html.replace(
        "window.enviarMensajeManual = async function (e, wa_id) {",
        "window.pendingUploads = [];\n        \n        window.renderPendingMediaUI = function() {\n            let qContainer = document.getElementById('pendingMediaQueue');\n            if (!qContainer) {\n                qContainer = document.createElement('div');\n                qContainer.id = 'pendingMediaQueue';\n                qContainer.className = 'media-queue-container';\n                const chatInputWrap = document.querySelector('.chat-input-wrapper');\n                chatInputWrap.parentNode.insertBefore(qContainer, chatInputWrap);\n            }\n            \n            if (window.pendingUploads.length === 0) {\n                qContainer.style.display = 'none';\n                return;\n            }\n            \n            qContainer.style.display = 'flex';\n            qContainer.innerHTML = '';\n            window.pendingUploads.forEach((up, idx) => {\n                const el = document.createElement('div');\n                el.className = 'media-queue-item';\n                \n                if (up.file && up.file.type.startsWith('image/')) {\n                    el.style.backgroundImage = url(\);\n                } else {\n                    el.style.background = '#333';\n                    el.innerHTML = '<div style=\"display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-size:24px;\">??</div>';\n                }\n                \n                if (idx === 0) {\n                    const badge = document.createElement('div');\n                    badge.innerText = 'Texto';\n                    badge.style.position = 'absolute';\n                    badge.style.bottom = '2px';\n                    badge.style.left = '2px';\n                    badge.style.fontSize = '10px';\n                    badge.style.background = 'var(--primary-color)';\n                    badge.style.color = 'white';\n                    badge.style.padding = '0px 4px';\n                    badge.style.borderRadius = '3px';\n                    el.appendChild(badge);\n                }\n\n                if (up.error) {\n                    el.style.border = '2px solid red';\n                } else if (!up.media_id) {\n                    const ld = document.createElement('div');\n                    ld.className = 'media-queue-loading';\n                    ld.innerHTML = '<svg width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" class=\"spin-anim\"><circle cx=\"12\" cy=\"12\" r=\"10\"></circle><path d=\"M12 6v6l4 2\"></path></svg>';\n                    el.appendChild(ld);\n                }\n\n                const rm = document.createElement('button');\n                rm.className = 'media-queue-remove';\n                rm.innerHTML = 'X';\n                rm.onclick = () => {\n                    window.pendingUploads.splice(idx, 1);\n                    window.renderPendingMediaUI();\n                };\n                el.appendChild(rm);\n                \n                qContainer.appendChild(el);\n            });\n        };\n\n        window.enviarMensajeManual = async function (e, wa_id) {"
    )

# update enviarMensajeManual to queue handle
envMan_old = r'''window.enviarMensajeManual = async function \(e, wa_id\) \{
            e.preventDefault\(\);
            const input = document.getElementById\('manualMsgInput'\);
            if \(\!input\) return;
            const msj = input.value.trim\(\);
            if \(\!msj\) return;

            // Vaciar y enfocar
            input.value = '';
            input.focus\(\);

            // Dibujado optimista instantáneo
            const scroll = document.getElementById\('chatScroll'\);
            if \(scroll\) \{
                const bubble = document.createElement\('div'\);
                bubble.className = "bubble bubble-bot lado-der";
                bubble.style.border = "1px solid var\(--primary-color\)";
                bubble.innerText = msj;
                scroll.appendChild\(bubble\);
                scroll.scrollTop = scroll.scrollHeight;
            \}'''

envMan_new = r'''window.enviarMensajeManual = async function (e, wa_id) {
            e.preventDefault();
            const input = document.getElementById('manualMsgInput');
            if (!input) return;
            const msj = input.value.trim();
            const hasPendingUploads = window.pendingUploads && window.pendingUploads.length > 0;
            
            if (!msj && !hasPendingUploads) return;

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

                // Clean the UI first since we generated the message payloads
                input.value = '';
                input.focus();
                window.pendingUploads = [];
                window.renderPendingMediaUI();

                // Send first message
                await window._sendRawTextManual(firstMsgText, wa_id, msj || "[Archivos enviados]");

                // Send remaining messages sequentially
                for (let rMsg of remainingMessages) {
                    await window._sendRawTextManual(rMsg, wa_id, "");
                }
                setTimeout(() => window.location.reload(), 500);
                return;
            }

            // Normal text
            input.value = '';
            input.focus();
            await window._sendRawTextManual(msj, wa_id, msj);
        };

        window._sendRawTextManual = async function(rawPayload, wa_id, optimisticText) {
            const scroll = document.getElementById('chatScroll');
            let bubble = null;
            if (scroll && optimisticText) {
                bubble = document.createElement('div');
                bubble.className = "bubble bubble-bot lado-der";
                bubble.style.border = "1px solid var(--primary-color)";
                bubble.innerText = optimisticText;
                scroll.appendChild(bubble);
                scroll.scrollTop = scroll.scrollHeight;
            }'''
html = re.sub(envMan_old, envMan_new, html, flags=re.DOTALL)

call_old = r'''const res = await fetch\('/api/admin/enviar_manual', \{
                    method: 'POST',
                    headers: \{ 'Content-Type': 'application/json' \},
                    body: JSON.stringify\(\{ wa_id: wa_id, texto: msj, reply_to_wamid: replyWamid, quick_reply_title: qrTitleToPass \}\)
                \}\);'''

call_new = r'''const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: rawPayload, reply_to_wamid: replyWamid, quick_reply_title: qrTitleToPass })
                });'''
html = re.sub(call_old, call_new, html, flags=re.DOTALL)

uploadMedia_old = r'''const uploadMedia = async \(file, mode = 'imagen'\) => \{
            const wa_id = window.location.pathname.split\('/'\).pop\(\);
            if \(\!wa_id \|\| isNaN\(wa_id\) \|\| wa_id === 'inbox'\) \{
                alert\("Debes tener un chat abierto para enviar multimedia directamente."\);
                return;
            \}

            // Comprimir imagen pesada desde el navegador ANTES de subir para no saturar a Nginx/Meta
            const compressImage = async \(inputFile\) => \{.*?return new Promise\(\(resolve\) => \{.*?\};\n            \};\n\n            if \(mode === 'imagen'\) \{\n                file = await compressImage\(file\);\n            \}\n\n            let modeIcon = mode === 'video' \? '??' : mode === 'audio' \? '??' : '???';\n\n            // Dibujado de burbuja temporal "cargando" para liberar el UI general\n            const scroll = document.getElementById\('chatScroll'\);\n            let loadingBubble = null;\n            if \(scroll\) \{.*?\n                scroll.appendChild\(loadingBubble\);\n                scroll.scrollTop = scroll.scrollHeight;\n            \}\n\n            const formData = new FormData\(\);\n            formData.append\("file", file\);\n            formData.append\("mode", mode\);\n\n            try \{\n                // Sube el archivo de forma completamente asíncrona a nuestro servidor\n                const uploadRes = await fetch\('/api/admin/upload_media', \{\n                    method: 'POST',\n                    body: formData\n                \}\);\n\n                const uploadData = await uploadRes.json\(\);\n                if \(\!uploadData.ok\) \{\n                    if \(scroll && scroll.lastChild === loadingBubble\) \{\n                        loadingBubble.innerHTML = <span style="color:var\(--danger-color\);">? Falló subida: \$\{uploadData.error || 'Inválido'\}</span>;\n                    \}\n                    alert\("Error del servidor subiendo: " \+ \(uploadData.error \|\| "Desconocido"\)\);\n                    return;\n                \}\n\n                const media_id = uploadData.media_id;\n                if \(scroll && scroll.lastChild === loadingBubble\) \{\n                    scroll.removeChild\(loadingBubble\);\n                \}\n\n                // Despachar el payload a whatsapp silenciosamente\n                const msjFake = \[\$\{mode\}:\$\{media_id\}\];\n                await fetch\('/api/admin/enviar_manual', \{\n                    method: 'POST',\n                    headers: \{ 'Content-Type': 'application/json' \},\n                    body: JSON.stringify\(\{ wa_id: wa_id, texto: msjFake \}\)\n                \}\);\n                \n                // Forzar polling acelerado local\n                setTimeout\(\(\) => pulseScroll\(true\), 1000\);\n\n            \} catch \(e\) \{\n                console.error\("Fallo de red al enviar media:", e\);\n                if \(scroll && scroll.lastChild === loadingBubble\) \{\n                    scroll.removeChild\(loadingBubble\);\n                \}\n                alert\("Error de red conectando con el panel Web para subir archivo."\);\n            \}\n        \};'''

uploadMedia_new = r'''const uploadMedia = async (file, mode = 'imagen') => {
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
html = re.sub(uploadMedia_old, uploadMedia_new, html, flags=re.DOTALL)

with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(html)
