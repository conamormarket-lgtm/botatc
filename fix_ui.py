import re
with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old_direct = '''window.enviarMensajeDirecto = async function(wa_id, msj) {
            if (!msj) return;
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            try {
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
                });

                const data = await res.json();
                if(!data.ok) { console.error("Error direct send json", data); }
            } catch(e) {
                console.error("Error direct send", e);
            }
        };'''

new_direct = '''window.enviarMensajeDirecto = async function(wa_id, msj) {
            if (!msj) return {ok: false};
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            try {
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
                });

                const data = await res.json();
                if(!data.ok) { console.error("Error direct send json", data); }
                return data;
            } catch(e) {
                console.error("Error direct send", e);
                return {ok: false, error: e};
            }
        };'''

text = text.replace(old_direct, new_direct)

old_audio = '''                                if(data.ok && data.media_id) {
                                    window.enviarMensajeDirecto(wa_id, `[audio:${data.media_id}]`, null);
                                    // Append locally artificially just for UX
                                    const c = document.getElementById('chatScroll');
                                    if(c) {
                                        const div = document.createElement('div');
                                        div.className = 'bubble bubble-out';
                                        div.innerHTML = `<div class="bubble-content" style="background:var(--primary-color);color:white;padding:0.8rem;border-radius:12px;"><span style="font-size:1.5rem;">🎤</span> <span style="font-size:0.9rem;">Audio enviado</span></div>`;
                                        c.appendChild(div);
                                        c.scrollTop = c.scrollHeight;
                                    }
                                }'''

new_audio = '''                                if(data.ok && data.media_id) {
                                    const enviaRes = await window.enviarMensajeDirecto(wa_id, `[audio:${data.media_id}]`, null);
                                    if(enviaRes && enviaRes.ok) {
                                        // Append locally artificially just for UX
                                        const c = document.getElementById('chatScroll');
                                        if(c) {
                                            const div = document.createElement('div');
                                            div.className = 'bubble bubble-out';
                                            div.innerHTML = `<div class="bubble-content" style="background:var(--primary-color);color:white;padding:0.8rem;border-radius:12px;"><span style="font-size:1.5rem;">🎤</span> <span style="font-size:0.9rem;">Audio enviado</span></div>`;
                                            c.appendChild(div);
                                            c.scrollTop = c.scrollHeight;
                                        }
                                    } else {
                                        alert("El servidor de WhatsApp (Meta) rechazó o no pudo procesar el formato del audio.");
                                    }
                                }'''

text = text.replace(old_audio, new_audio)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated UI logic to await API confirmation")
