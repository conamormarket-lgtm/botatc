import re

# 1. Update server.py to add the HTML button next to "Enviar"
with open("server.py", "r", encoding="utf-8") as f:
    server_text = f.read()

old_btn = '''<button type="submit" style="background:var(--primary-color);color:white;border:none;border-radius:12px;padding:0 1.5rem;height:44px;font-weight:600;font-size:0.95rem;cursor:pointer;transition:background 0.2s;">Enviar</button>'''
new_btn = '''<button type="button" id="btnRecordAudio" style="background:var(--accent-bg); color:var(--text-main); border:none; border-radius:12px; height:44px; width:44px; display:flex; align-items:center; justify-content:center; cursor:pointer; margin-left: 0.5rem; margin-right: 0.5rem; transition: background 0.2s, color 0.2s;" title="Grabar nota de voz">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                </button>
                <button type="submit" style="background:var(--primary-color);color:white;border:none;border-radius:12px;padding:0 1.5rem;height:44px;font-weight:600;font-size:0.95rem;cursor:pointer;transition:background 0.2s;">Enviar</button>'''

if 'btnRecordAudio' not in server_text:
    server_text = server_text.replace(old_btn, new_btn)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(server_text)

# 2. Update inbox.html to add JS Logic using event delegation
with open("inbox.html", "r", encoding="utf-8") as f:
    inbox_text = f.read()

js_logic = '''
        // NATIVE AUDIO RECORDING LOGIC
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        document.addEventListener('click', async function(e) {
            const btnRecord = e.target.closest('#btnRecordAudio');
            if(btnRecord) {
                if(!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        mediaRecorder.addEventListener("dataavailable", event => {
                            if(event.data.size > 0) audioChunks.push(event.data);
                        });
                        mediaRecorder.addEventListener("stop", async () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
                            const formData = new FormData();
                            formData.append("file", audioBlob, "voice_note.webm");
                            
                            const wa_id = window.location.pathname.split('/').pop();
                            
                            // Visual feedback
                            const manualInput = document.getElementById("manualMsgInput");
                            if(manualInput) {
                                manualInput.value = "📤 Subiendo audio...";
                                manualInput.disabled = true;
                            }

                            try {
                                const res = await fetch('/api/admin/upload_media', {
                                    method: 'POST',
                                    body: formData
                                });
                                const data = await res.json();
                                if(manualInput) {
                                    manualInput.value = "";
                                    manualInput.disabled = false;
                                }
                                if(data.ok && data.media_id) {
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
                                } else {
                                    alert("Error subiendo el audio a los servidores de WhatsApp");
                                }
                            } catch(err) {
                                if(manualInput) manualInput.disabled = false;
                                alert("Fallo de red al enviar el audio.");
                            }
                        });
                        mediaRecorder.start();
                        isRecording = true;
                        
                        btnRecord.style.background = "#ef4444";
                        btnRecord.style.color = "white";
                        btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
                        
                        // Opcional: Mostrar que está grabando en el input
                        const manualInput = document.getElementById("manualMsgInput");
                        if(manualInput) {
                            manualInput.dataset.originalPlaceholder = manualInput.placeholder;
                            manualInput.placeholder = "🔴 Grabando audio... (Presiona el cuadro rojo para detener/enviar)";
                        }

                    } catch(err) {
                        alert("Es necesario otorgar permisos de micrófono al navegador para grabar audios.");
                    }
                } else {
                    // Stop recording (this triggers the "stop" event listener above to send the message)
                    mediaRecorder.stop();
                    isRecording = false;
                    mediaRecorder.stream.getTracks().forEach(t => t.stop());
                    
                    btnRecord.style.background = "var(--accent-bg)";
                    btnRecord.style.color = "var(--text-main)";
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    
                    const manualInput = document.getElementById("manualMsgInput");
                    if(manualInput && manualInput.dataset.originalPlaceholder) {
                        manualInput.placeholder = manualInput.dataset.originalPlaceholder;
                    }
                }
            }
        });
'''

if 'btnRecordAudio' not in inbox_text:
    # Just inject it before `window.enviarMensajeDirecto = async function`
    inbox_text = inbox_text.replace("window.enviarMensajeDirecto = async function", js_logic + "\n\n        window.enviarMensajeDirecto = async function")
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(inbox_text)

print("Audio recording setup complete")
