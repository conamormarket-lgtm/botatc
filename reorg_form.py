import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx1 = text.find('<form onsubmit="window.enviarMensajeManual')
if idx1 == -1:
    print("Form not found")
    import sys; sys.exit(1)
idx2 = text.find('</form>', idx1) + 7

original_form = text[idx1:idx2]

new_form = r"""<form onsubmit="window.enviarMensajeManual(event, '{wa_id}'); return false;" style="display:flex; gap:0.5rem; width:100%; margin:0; position:relative; align-items:center; box-sizing:border-box; max-width:100%;">
                <input type="hidden" id="replyToWamid" value="">
                
                <!-- IZQUIERDA: Emojis y Stickers -->
                <div style="flex:0 0 auto; display:flex; gap:0.1rem;">
                    <!-- Emoji Button -->
                    <button type="button" onclick="const m = document.getElementById('emojiMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Emojis">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                    </button>
                    <!-- Sticker Button -->
                    <button type="button" onclick="const m = document.getElementById('stickerMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Stickers">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5"></path><path d="M8.5 8.5v.01"></path><path d="M16 15.5v.01"></path><path d="M12 12v.01"></path><path d="M11 17a4.5 4.5 0 0 0 5-3"></path></svg>
                    </button>
                </div>

                <!-- CENTRO: Input + Iconos internos -->
                <div style="flex:1; display:flex; align-items:center; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:30px; padding:0.2rem 0.6rem; position:relative;">
                    
                    <!-- attach menu invisible pero insertado antes para dom tree relative -->
                    <div id="attachMenu" style="display:none; position:absolute; bottom:calc(100% + 0.8rem); right:60px; width:190px; background:var(--accent-bg); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.5); padding:0.5rem; flex-direction:column; gap:0.2rem; z-index:100;">
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').removeAttribute('capture'); document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg> Subir Imagen
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'video'); document.getElementById('hiddenFileInput').accept='video/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg> Subir Video
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'audio'); document.getElementById('hiddenFileInput').accept='audio/*'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg> Subir Audio
                        </button>
                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; document.getElementById('hiddenFileInput').setAttribute('data-mode', 'documento'); document.getElementById('hiddenFileInput').accept='.pdf,.doc,.docx,.xls,.xlsx,.txt'; document.getElementById('hiddenFileInput').click();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Subir Documento
                        </button>
                    </div>

                    <input type="text" id="manualMsgInput" placeholder="Mensaje..." style="flex:1; min-width:0; background:transparent; border:none; outline:none; color:var(--text-main); font-size:1rem; padding:0.6rem 0.2rem; font-family:var(--font-main);" autocomplete="off" oninput="checkQuickReplyTrigger(this); if(window.toggleSendMicButton) window.toggleSendMicButton();">
                    
                    <!-- Clip (Adjuntos) -->
                    <button type="button" onclick="const m = document.getElementById('attachMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Adjuntar">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transform: rotate(45deg);"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                    </button>
                    <!-- Cámara -->
                    <button type="button" onclick="document.getElementById('hiddenFileInput').setAttribute('data-mode', 'imagen'); document.getElementById('hiddenFileInput').accept='image/*'; document.getElementById('hiddenFileInput').setAttribute('capture', 'environment'); document.getElementById('hiddenFileInput').click();" style="background:transparent; border:none; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Cámara">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>
                    </button>
                    <!-- Rayo (Respuestas) -->
                    <button type="button" onclick="const side = document.getElementById('rightSidebar'); side.style.display = side.style.display==='none'?'flex':'none'; if(side.style.display==='flex') cargarQuickReplies();" style="background:transparent; border:none; width:36px; height:36px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--accent-hover); transition:color 0.2s;" onmouseover="this.style.color='var(--primary-color)'" onmouseout="this.style.color='var(--accent-hover)'" title="Respuestas Rápidas">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                    </button>
                </div>

                <!-- DERECHA: Mic o Send -->
                <div style="flex:0 0 auto; display:flex; align-items:center; gap:0.2rem;">
                    <!-- Send Button (Toggle) -->
                    <button type="submit" id="btnSubmitForm" style="background:var(--primary-color);color:white;border:none;border-radius:50%;width:46px;height:46px;display:none;align-items:center;justify-content:center;cursor:pointer;transition:transform 0.2s; box-shadow:0 3px 5px rgba(0,0,0,0.2);" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'" title="Enviar">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none" style="margin-left: 2px;"><line x1="22" y1="2" x2="11" y2="13" stroke="white" stroke-width="2"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                    <!-- Record Audio Button (Toggle) -->
                    <button type="button" id="btnRecordAudio" style="background:var(--primary-color);color:white;border:none;border-radius:50%;width:46px;height:46px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:transform 0.2s; box-shadow:0 3px 5px rgba(0,0,0,0.2);" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'" title="Grabar nota de voz">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
                    </button>
                    <!-- Cancel Audio -->
                    <button type="button" id="btnCancelAudio" style="background:var(--danger-color); color:white; border:none; border-radius:50%; height:46px; width:46px; display:none; align-items:center; justify-content:center; cursor:pointer; transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'" title="Cancelar grabación">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>
            </form>"""

text = text.replace(original_form, new_form)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Exchanged form layout.")
