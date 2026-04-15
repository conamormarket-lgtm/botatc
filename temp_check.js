// FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            // Auto seleccionar el mensaje al que dimos click derecho
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks during selection
        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true); // Use capture phase!

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            // Load frequent chats
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un n\u00famero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert(\u00A1Enviado! Mensajes enviados a  + data.count +  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error:  + (data.error || 'Algo sali\u00F3 mal'));
                }
            } catch(e) {
                alert("Error de red enviando petici\u00F3n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

        // CHAT LIST CONTEXT MENU
        let ctxChatNum = null;
        window.showChatMenu = function(e, num, isArchived, isPinned) {
            e.preventDefault();
            ctxChatNum = num;
            // Manejar tanto string como boolean que pueda mandar Python
            let arch = (isArchived === true || isArchived === "true");
            let pin = (isPinned === true || isPinned === "true");
            
            document.getElementById('btnArchivar').innerText = arch ? 'Desarchivar chat' : 'Archivar chat';
            document.getElementById('btnFijar').innerText = pin ? 'Desfijar chat' : 'Fijar chat';
            
            let menu = document.getElementById('chatListMenu');
            menu.style.display = 'flex';
            menu.style.left = e.clientX + 'px';
            menu.style.top = e.clientY + 'px';
            return false;
        };

        window.chatAction = async function(action) {
            if(!ctxChatNum) return;
            if(action === 'delete') {
                const modalHtml = `
                    <div id="deleteConfirmModal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:10000; display:flex; align-items:center; justify-content:center;">
                        <div style="background:var(--bg-main); padding:2rem; border-radius:12px; max-width:400px; text-align:center; border:1px solid var(--accent-border);">
                            <h3 style="margin-top:0; color:#ef4444;">Ã‚Â¿Borrar este chat?</h3>
                            <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:1.5rem;">Esta acciÃƒÂ³n eliminarÃƒÂ¡ el chat permanentemente y no se puede deshacer.</p>
                            <div style="display:flex; justify-content:center; gap:1rem;">
                                <button onclick="document.body.removeChild(document.getElementById('deleteConfirmModal'))" style="padding:0.6rem 1.5rem; border-radius:8px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); cursor:pointer;">Cancelar</button>
                                <button onclick="window.confirmDeleteChat()" style="padding:0.6rem 1.5rem; border-radius:8px; border:none; background:#ef4444; color:white; cursor:pointer;">Borrar Permanente</button>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                document.getElementById('chatListMenu').style.display = 'none';
                return;
            }
            
            await executeChatAction(action);
        };

        window.confirmDeleteChat = async function() {
            const modal = document.getElementById('deleteConfirmModal');
            if(modal) document.body.removeChild(modal);
            await executeChatAction('delete');
        };

        async function executeChatAction(action) {
            try {
                const res = await fetch("/api/admin/chat/action", {
                    method: "POST",
                    headers: {"Content-Type":"application/json"},
                    body: JSON.stringify({wa_id: ctxChatNum, action: action})
                });
                if(res.ok) {
                    if (action === 'unread' && ctxChatNum === curWaId) {
                        window.location.href = '/inbox';
                    } else {
                        window.location.reload();
                    }
                } else {
                    alert('Error realizando accin');
                }
            } catch(e) {
                console.error(e);
            }
            document.getElementById('chatListMenu').style.display = 'none';
        }

        document.addEventListener('click', function(e) {
            let menu1 = document.getElementById('chatListMenu');
            if(menu1 && !menu1.contains(e.target)) menu1.style.display = 'none';
        });

        // LOGICA DE MENÃƒÅ¡s CONTEXTUAL
        let ctxTargetWamid = "";
        let ctxTargetText = "";
        let ctxTargetMediaId = "";
        let ctxTargetBubble = null;
        let ctxTargetImageUrl = "";
        let ctxTargetAudioUrl = "";

        document.addEventListener("contextmenu", function (e) {
            const bubble = e.target.closest('.bubble');
            if (bubble) {
                e.preventDefault(); // Evitamos menÃƒÂº del navegador

                ctxTargetWamid = bubble.getAttribute('data-wamid');
                ctxTargetBubble = bubble;
                
                // Show InformaciÃƒÂ³n only for bot messages with data-sent-by
                const infoItem = document.getElementById('ctxMsgInfo');
                if (infoItem) {
                    infoItem.style.display = bubble.classList.contains('bubble-bot') && bubble.dataset.sentBy !== undefined ? 'flex' : 'none';
                }
                ctxTargetText = bubble.innerText;

                let clickedImg = e.target.closest('img');
                let stickerImg = null;
                let regularImg = null;

                if (clickedImg && clickedImg.getAttribute('alt')) {
                    if (clickedImg.getAttribute('alt').startsWith("Sticker")) {
                        stickerImg = clickedImg;
                    } else if (clickedImg.getAttribute('alt').startsWith("Imagen")) {
                        regularImg = clickedImg;
                    }
                } else {
                    stickerImg = bubble.querySelector('img[alt^="Sticker"]');
                    regularImg = bubble.querySelector('img[alt^="Imagen"]');
                }

                let ctxSaveSticker = document.getElementById("ctxSaveSticker");
                if (stickerImg) {
                    ctxTargetMediaId = stickerImg.getAttribute('alt').replace('Sticker ', '').trim();
                    ctxSaveSticker.style.display = 'flex';
                } else {
                    ctxTargetMediaId = "";
                    ctxSaveSticker.style.display = 'none';
                }

                let ctxCopyImage = document.getElementById("ctxCopyImage");
                let ctxDownloadImage = document.getElementById("ctxDownloadImage");
                if (regularImg && !stickerImg) {
                    ctxTargetImageUrl = regularImg.src;
                    ctxCopyImage.style.display = 'flex';
                    ctxDownloadImage.style.display = 'flex';
                } else {
                    ctxTargetImageUrl = "";
                    ctxCopyImage.style.display = 'none';
                    ctxDownloadImage.style.display = 'none';
                }

                let clickedAudio = e.target.closest('.custom-audio-player') ? e.target.closest('.custom-audio-player').querySelector('audio') : bubble.querySelector('audio');
                let ctxDownloadAudio = document.getElementById('ctxDownloadAudio');
                if (clickedAudio) {
                    ctxTargetAudioUrl = clickedAudio.src;
                    if(ctxDownloadAudio) ctxDownloadAudio.style.display = 'flex';
                } else {
                    ctxTargetAudioUrl = "";
                    if(ctxDownloadAudio) ctxDownloadAudio.style.display = 'none';
                }

                const cm = document.getElementById("bubbleContextMenu");
                cm.style.display = "block";

                let x = e.clientX;
                let y = e.clientY;

                if (x + cm.offsetWidth > window.innerWidth) x = window.innerWidth - cm.offsetWidth - 10;
                if (y + cm.offsetHeight > window.innerHeight) y = window.innerHeight - cm.offsetHeight - 10;

                cm.style.left = x + "px";
                cm.style.top = y + "px";

                const ctxReply = document.getElementById("ctxReply");
                if (ctxTargetWamid) {
                    ctxReply.style.opacity = "1";
                    ctxReply.style.pointerEvents = "auto";
                } else {
                    ctxReply.style.opacity = "0.4";
                    ctxReply.style.pointerEvents = "none";
                }
            }
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest('#bubbleContextMenu')) {
                document.getElementById("bubbleContextMenu").style.display = "none";
            }
        });

        document.getElementById("ctxReply").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            if (ctxTargetWamid) {
                const h = document.getElementById('replyToWamid');
                const p = document.getElementById('replyPreviewContainer');
                const t = document.getElementById('replyPreviewTxt');
                if (h && p && t) {
                    h.value = ctxTargetWamid;
                    t.innerText = ctxTargetText.substring(0, 40) + '...';
                    p.style.display = 'flex';
                    document.getElementById('manualMsgInput').focus();
                }
            }
        });

        document.getElementById("ctxQuote").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            const i = document.getElementById('manualMsgInput');
            if (i) {
                i.value = "> " + ctxTargetText.trim() + "\n\n" + i.value;
                i.focus();
            }
        });

        document.getElementById("ctxCopy").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            navigator.clipboard.writeText(ctxTargetText.trim());
        });

        document.getElementById("ctxCopyImage").addEventListener("click", async function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            if (!ctxTargetImageUrl) return;
            try {
                const img = new Image();
                img.crossOrigin = "Anonymous";
                img.src = ctxTargetImageUrl;
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                });
                
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(async (blob) => {
                    try {
                        await navigator.clipboard.write([
                            new ClipboardItem({
                                'image/png': blob
                            })
                        ]);
                    } catch(err) {
                        console.error("Clipboard API error", err);
                        alert("El navegador bloqueÃƒÂ³ la copia de la imagen.");
                    }
                }, 'image/png');
            } catch(e) {
                console.error("Error copy image", e);
                alert("No se pudo copiar la imagen.");
            }
        });

        document.getElementById('ctxDownloadAudio')?.addEventListener('click', function () {
            document.getElementById('bubbleContextMenu').style.display = 'none';
            if (ctxTargetAudioUrl && window.descargarMedia) {
                window.descargarMedia(ctxTargetAudioUrl, 'audio_whatsapp.ogg');
            }
        });

        document.getElementById("ctxDownloadImage").addEventListener("click", async function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            if (!ctxTargetImageUrl) return;
            try {
                const response = await fetch(ctxTargetImageUrl);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.style.display = "none";
                a.href = url;
                // Generar nombre descriptivo con timestamp
                a.download = "imagen_atc_" + Date.now() + ".png";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch(e) {
                console.error("Error downloading image", e);
                alert("OcurriÃƒÂ³ un error al descargar la imagen.");
            }
        });

        async function enviarReaccion(emojiStr) {
            document.getElementById("bubbleContextMenu").style.display = "none";
            if (!ctxTargetWamid) return alert("Ã¢ÂÅ’ Este mensaje no se puede reaccionar");

            const wa_id = window.location.pathname.split('/').pop(); // /inbox/519...
            try {
                const res = await fetch('/api/admin/reaccionar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, message_id: ctxTargetWamid, emoji: emojiStr })
                });
                const data = await res.json();
                if (!data.ok) {
                    alert("Ã¢ÂÅ’ Error: " + data.error);
                }
            } catch (e) {
                alert("Ã¢ÂÅ’ Falla de conectividad");
            }
        }

        document.getElementById("ctxSaveSticker").addEventListener("click", async function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            if (!ctxTargetMediaId) return;

            // Notification toast provisional
            let originalText = this.innerHTML;

            try {
                const res = await fetch('/api/admin/stickers/save_from_media', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ media_id: ctxTargetMediaId })
                });
                const data = await res.json();
                if (data.ok) {
                    alert("Ã¢Â­Â Sticker guardado en tus favoritos extra (Firebase) con ÃƒÂ©xito!");
                    toggleStickersMenu(); toggleStickersMenu(); // refresh silently
                } else {
                    alert("Ã¢ÂÅ’ Error guardando sticker: " + data.error);
                }
            } catch (e) {
                alert("Ã¢ÂÅ’ Falla de conectividad");
            }
        });
        // DOM AJAX REFRESHER PARA LIVE CHAT (Mantiene posiciÃƒÂ³n del scroll y reemplaza listas suavemente)
        setInterval(async () => {
            try {
                // Prevenir cachÃƒÂ© del navegador
                const url = window.location.href;
                const fetchUrl = url + (url.includes('?') ? '&' : '?') + 't=' + new Date().getTime() + '&ajax=1';

                const res = await fetch(fetchUrl, {
                    cache: 'no-store',
                    headers: { 'Cache-Control': 'no-cache' }
                });

                const text = await res.text();
                const doc = new DOMParser().parseFromString(text, 'text/html');

                // Actualizar Lista de Conversaciones
                const newChats = doc.querySelector('.chats-container');
                const oldChats = document.querySelector('.chats-container');
                if (newChats && oldChats && oldChats.innerHTML !== newChats.innerHTML) {
                    oldChats.innerHTML = newChats.innerHTML;
                    if (typeof window.aplicarFiltroChats === 'function') {
                        window.aplicarFiltroChats();
                    }
                }

                // Actualizar visibilidad de Chat
                const newScroll = doc.getElementById('chatScroll');
                const oldScroll = document.getElementById('chatScroll');
                if (newScroll && oldScroll) {
                    const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
                    let didAppend = false;
                    
                    // Aislar temporalmente elementos de subida asÃƒÂ­ncrona (fantasmas)
                    const tempNodes = Array.from(oldScroll.querySelectorAll('[data-temp="true"]'));
                    tempNodes.forEach(node => oldScroll.removeChild(node));
                    
                    const cleanHTML = (html) => html.replace(/style="[^"]*"/g, "").replace(/>\d+:\d{2}</g, ">0:00<");
                    
                    const newChildren = Array.from(newScroll.children);
                    
                    for (let i = 0; i < newChildren.length; i++) {
                        const newNode = newChildren[i];
                        const oldNode = oldScroll.children[i];
                        
                        if (!oldNode) {
                            oldScroll.appendChild(newNode.cloneNode(true));
                            didAppend = true;
                        } else {
                            if (cleanHTML(oldNode.innerHTML) !== cleanHTML(newNode.innerHTML)) {
                                const audio = oldNode.querySelector('audio');
                                if (audio && window._currentAudio === audio && !audio.paused) {
                                    continue;
                                }
                                oldScroll.replaceChild(newNode.cloneNode(true), oldNode);
                            }
                        }
                    }
                    
                    while (oldScroll.children.length > newChildren.length) {
                        oldScroll.removeChild(oldScroll.lastChild);
                    }
                    
                    // Reinyectar elementos asÃƒÂ­ncronos fantasma
                    tempNodes.forEach(node => oldScroll.appendChild(node));
                    
                    if (didAppend && isAtBottom) {
                        oldScroll.scrollTop = oldScroll.scrollHeight;
                    }
                }
            } catch (e) {
                console.warn('Error en Live Chat Polling:', e);
            }
        }, 1500);

        // API CLIENT PARA RESPONDER
        
        
        // NATIVE AUDIO RECORDING LOGIC
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        window._isAudioRecording = false;

        document.addEventListener('click', async function(e) {
            const btnRecord = e.target.closest('#btnRecordAudio');
            if(btnRecord) {
                if(!isRecording) {
                    try {
                        window._isAudioRecording = true;
                        if(window.toggleSendMicButton) window.toggleSendMicButton();
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);
                        audioChunks = [];
                        mediaRecorder.addEventListener("dataavailable", event => {
                            if(event.data.size > 0) audioChunks.push(event.data);
                        });
                        mediaRecorder.addEventListener("stop", async () => {
                            if (mediaRecorder.canceled) {
                                return; // Do not send audio if canceled
                            }
                            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' }); // WebM/OGG format for audio
                            const formData = new FormData();
                            formData.append("file", audioBlob, "voice_note.webm");
                            
                            const wa_id = window.location.pathname.split('/').pop();
                            
                            // Visual feedback
                            const manualInput = document.getElementById("manualMsgInput");
                            if(manualInput) {
                                manualInput.value = "Ã°Å¸â€œÂ¤ Subiendo audio...";
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
                                    const enviaRes = await window.enviarMensajeDirecto(wa_id, `[audio:${data.media_id}]`, null);
                                    if(enviaRes && enviaRes.ok) {
                                        // Append locally artificially just for UX
                                        const c = document.getElementById('chatScroll');
                                        if(c) {
                                            const div = document.createElement('div');
                                            div.className = 'bubble bubble-bot lado-der';
                                            div.innerHTML = `<div class="bubble-content" style="background:var(--primary-color);color:white;padding:0.8rem;border-radius:12px;"><span style="font-size:1.5rem;">Ã°Å¸Å½Â¤</span> <span style="font-size:0.9rem;">Audio enviado</span></div>`;
                                            c.appendChild(div);
                                            c.scrollTop = c.scrollHeight;
                                        }
                                    } else {
                                        alert("El servidor de WhatsApp (Meta) rechazÃƒÂ³ o no pudo procesar el formato del audio.\n\nDetalle tÃƒÂ©cnico: " + (enviaRes?.error || "Desconocido"));
                                    }
                                } else {
                                    alert("Error procesando o subiendo el audio:\n\n" + (data.error || "Rechazo desconocido en el servidor."));
                                }
                            } catch(err) {
                                if(manualInput) manualInput.disabled = false;
                                alert("Fallo de red al enviar el audio.");
                            }
                        });
                        mediaRecorder.start();
                        mediaRecorder.canceled = false;
                        isRecording = true;
                        if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'flex';
                        
                        btnRecord.style.background = "#ef4444";
                        btnRecord.style.color = "white";
                        btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>`;
                        
                        // Opcional: Mostrar que estÃƒÂ¡ grabando en el input
                        const manualInput = document.getElementById("manualMsgInput");
                        if(manualInput) {
                            manualInput.dataset.originalPlaceholder = manualInput.placeholder;
                            manualInput.placeholder = "Ã°Å¸â€Â´ Grabando audio... (Presiona el cuadro rojo para detener/enviar)";
                        }

                    } catch(err) {
                        console.error('Audio Recorder Error:', err);
                        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                            alert("Ã¢ÂÅ’ Ã‚Â¡ConexiÃƒÂ³n Insegura! Tu navegador ha bloqueado el micrÃƒÂ³fono por seguridad. Las web de grabaciÃƒÂ³n de audio OBLIGAN a que uses 'https://' o entres desde 'http://localhost' en lugar de usar una IP directa de la red.");
                        } else {
                            alert("Permiso Denegado o Error: " + err.message + ". Verifica el candadito arriba a la izquierda y dale permisos al micrÃƒÂ³fono.");
                        }
                    }
                } else {
                    // Stop recording (this triggers the "stop" event listener above to send the message)
                    mediaRecorder.stop();
                    isRecording = false;
                    mediaRecorder.stream.getTracks().forEach(t => t.stop());
                    
                    btnRecord.style.background = "var(--accent-bg)";
                    btnRecord.style.color = "var(--text-main)";
                    if(document.getElementById('btnCancelAudio')) document.getElementById('btnCancelAudio').style.display = 'none';
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    
                    const manualInput = document.getElementById("manualMsgInput");
                    if(manualInput && manualInput.dataset.originalPlaceholder) {
                        manualInput.placeholder = manualInput.dataset.originalPlaceholder;
                    }
                }
            }
        });


        window._nextQuickReplyTitle = null;

        window.enviarMensajeDirecto = async function(wa_id, msj, qrTitle = null) {
            if (!msj) return {ok: false};
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            try {
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid, quick_reply_title: qrTitle || window._nextQuickReplyTitle || null })
                });

                const data = await res.json();
                if(!data.ok) { console.error("Error direct send json", data); }
                return data;
            } catch(e) {
                console.error("Error direct send", e);
                return {ok: false, error: e.message || "Red Error"};
            }
        };


                // Alternar boton enviar / grabar audio
        // CUSTOM AUDIO PLAYER LOGIC
        window.descargarMedia = function(url, filename) { const a = document.createElement('a'); a.href = url; a.download = filename || 'media_descargada'; document.body.appendChild(a); a.click(); document.body.removeChild(a); };
        window.formatAudioTime = function(seconds) {
            if (!seconds || isNaN(seconds)) return "0:00";
            const min = Math.floor(seconds / 60);
            const sec = Math.floor(seconds % 60);
            return min + ":" + (sec < 10 ? "0" : "") + sec;
        };

        window._currentAudio = null;
        window._currentBtn = null;
        window.toggleAudio = function(btn) {
            const container = btn.closest('.custom-audio-player');
            const audio = container.querySelector('audio');
            const iconPlay = btn.querySelector('.icon-play');
            const iconPause = btn.querySelector('.icon-pause');

            if (window._currentAudio && window._currentAudio !== audio) {
                window._currentAudio.pause();
                if (window._currentBtn) {
                    window._currentBtn.querySelector('.icon-play').style.display = 'block';
                    window._currentBtn.querySelector('.icon-pause').style.display = 'none';
                }
            }

            if (audio.paused) {
                audio.play();
                iconPlay.style.display = 'none';
                iconPause.style.display = 'block';
                window._currentAudio = audio;
                window._currentBtn = btn;
            } else {
                audio.pause();
                iconPlay.style.display = 'block';
                iconPause.style.display = 'none';
            }
        };

        window.seekAudio = function(e, timeline) {
            const container = timeline.closest('.custom-audio-player');
            const audio = container.querySelector('audio');
            if(!audio.duration || isNaN(audio.duration)) return;
            const rect = timeline.getBoundingClientRect();
            const percent = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1);
            audio.currentTime = percent * audio.duration;
            container.querySelector('.cap-progress').style.width = (percent * 100) + '%';
            container.querySelector('.cap-time').textContent = window.formatAudioTime(audio.currentTime);
        };

        window.autoResizeInput = function() {
            const el = document.getElementById('manualMsgInput');
            if(!el) return;
            el.style.height = '42px'; // Reset for recalculation
            const newHeight = Math.min(el.scrollHeight, 160);
            el.style.height = newHeight + 'px';
            el.style.overflowY = el.scrollHeight > 160 ? 'auto' : 'hidden';
            
            // Si regresa a 1 linea, asegura que este centrado todo
            if (newHeight <= 42) {
                el.style.paddingTop = '10px';
            }
        };

        window.toggleSendMicButton = function() {
            if (window._isAudioRecording) return; // No alternar si estamos grabando
            const input = document.getElementById('manualMsgInput');
            const submitMenu = document.getElementById('btnSubmitForm');
            const micMenu = document.getElementById('btnRecordAudio');
            
            const btnRightQR = document.getElementById('btnRightQR');
            const btnRightPhoto = document.getElementById('btnRightPhoto');
            
            if (input) {
                const hasText = input.value.trim().length > 0;
                
                if (submitMenu && micMenu) {
                    submitMenu.style.display = hasText ? 'flex' : 'none';
                    micMenu.style.display = hasText ? 'none' : 'flex';
                }
                
                if (btnRightQR) btnRightQR.style.display = hasText ? 'none' : 'flex';
                if (btnRightPhoto) btnRightPhoto.style.display = hasText ? 'none' : 'flex';
            }
        };

        // Escuchar input manual
        document.addEventListener('input', function(e) {
            if(e.target.id === 'manualMsgInput') {
                window.toggleSendMicButton();
            }
        });
        
        // Interceptar asignaciones programÃƒÂ¡ticas a value
        const originalValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
        setTimeout(() => {
            const msgInput = document.getElementById('manualMsgInput');
            if (msgInput && msgInput.__valueInterceptor !== true) {
                Object.defineProperty(msgInput, "value", {
                    set: function(val) {
                        originalValueSetter.call(this, val);
                        if (window.toggleSendMicButton) window.toggleSendMicButton();
                        if (window.autoResizeInput) window.autoResizeInput();
                    },
                    get: function() {
                        return Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").get.call(this);
                    }
                });
                msgInput.__valueInterceptor = true;
                if(window.toggleSendMicButton) window.toggleSendMicButton();
                if(window.autoResizeInput) window.autoResizeInput();
            }
        }, 1000); // Darle tiempo a la creacion del SPA
        
        window.enviarMensajeManual = async function (e, wa_id) {
            e.preventDefault();
            const input = document.getElementById('manualMsgInput');
            if (!input) return;
            const msj = input.value.trim();
            if (!msj) return;

            // Vaciar y enfocar
            input.value = '';
            input.focus();

            // Dibujado optimista instantÃƒÂ¡neo
            const scroll = document.getElementById('chatScroll');
            if (scroll) {
                const bubble = document.createElement('div');
                bubble.className = "bubble bubble-bot lado-der";
                bubble.style.border = "1px solid var(--primary-color)";
                bubble.innerText = msj;
                scroll.appendChild(bubble);
                scroll.scrollTop = scroll.scrollHeight;
            }

            const replyWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            if (document.getElementById('replyPreviewContainer')) {
                document.getElementById('replyPreviewContainer').style.display = 'none';
                if (document.getElementById('replyToWamid')) document.getElementById('replyToWamid').value = '';
            }

            try {
                const qrTitleToPass = window._nextQuickReplyTitle || null;
                window._nextQuickReplyTitle = null; // resetear
                
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyWamid, quick_reply_title: qrTitleToPass })
                });

                const data = await res.json();
                if (!data.ok) {
                    // Si fallÃƒÂ³ (ej: ventana de 24h de Meta API)
                    if (scroll && scroll.lastChild === bubble) {
                        scroll.removeChild(bubble);
                    }
                    if (data.error === "META_API_REJECTED") {
                        alert("Ã¢ÂÅ’ Error de WhatsApp (Meta): No puedes enviar mensajes libres a este nÃƒÂºmero porque no te ha escrito en las ÃƒÂºltimas 24 horas. Ã‚Â¡El cliente debe escribirte primero!");
                    } else {
                        alert("Ã¢ÂÅ’ Error no controlado al enviar: " + data.error);
                    }
                }
            } catch (e) {
                console.error("Fallo al enviar:", e);
                if (scroll && scroll.lastChild === bubble) {
                    scroll.removeChild(bubble);
                }
                alert("Error de red conectando con el panel Web o timeout.");
            }
        };

        // LIBRERÃƒÂA LOCAL DE STICKERS
        window.cargarStickers = async function () {
            const grid = document.getElementById('stickersGrid');
            if (!grid) return;
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5;">Cargando...</div>';
            try {
                const res = await fetch('/api/stickers');
                const data = await res.json();
                if (data.stickers && data.stickers.length > 0) {
                    grid.innerHTML = data.stickers.map(s =>
                        `<img src="/api/media/sticker/${s}" style="width:70px; height:70px; object-fit:contain; cursor:pointer; padding:5px; border-radius:8px; border:2px solid transparent; transition:border 0.2s;" onmouseover="this.style.border='2px solid var(--primary-color)'" onmouseout="this.style.border='2px solid transparent'" onclick="insertStickerLocal('${s}')" title="${s}">`
                    ).join('');
                } else {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5; font-size:0.85rem; color:var(--text-muted);">AÃƒÂºn no tienes stickers guardados.</div>';
                }
            } catch (e) { grid.innerHTML = '<div style="grid-column: 1/-1; padding:2rem; color:var(--danger-color);">Error cargando.</div>'; }
        };

        window.toggleStickersMenu = window.cargarStickers; // For backwards compat

        window.uploadStickerFromMenu = async function (input) {
            const file = input.files[0];
            if (!file) return;
            const grid = document.getElementById('stickersGrid');
            grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:2rem; opacity:0.5;">Ã¢ÂÂ³ Subiendo...</div>';
            const fd = new FormData();
            fd.append('files', file);
            try {
                const res = await fetch('/api/admin/stickers/upload', { method: 'POST', body: fd });
                if (res.ok) cargarStickers();
            } catch (e) { grid.innerHTML = '<div style="grid-column:1/-1; color:red;">Fallo al subir</div>'; }
        };

        window.insertStickerLocal = function (filename) {
            const input = document.getElementById('manualMsgInput');
            if (input) {
                input.value += `[sticker-local:${filename}] `;
                const m = document.getElementById('combinedEmojiMenu');
                if (m) m.style.display = 'none';

                // Auto-enviar la etiqueta (sticker)
                if(window.toggleSendMicButton) window.toggleSendMicButton(); // Fuerza a mostrar el btn de Enviar
                
                const form = input.closest('form');
                if (form) {
                    const btn = form.querySelector('button[type="submit"]');
                    if (btn) btn.click();
                    else form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                }
            }
        };

        // LÃƒâ€œGICA DE SUBIDA MULTIMEDIA ASÃƒÂNCRONA EN SEGUNDO PLANO
        const uploadMedia = async (file, mode = 'imagen') => {
            const wa_id = window.location.pathname.split('/').pop();
            if (!wa_id || isNaN(wa_id) || wa_id === 'inbox') {
                alert("Debes tener un chat abierto para enviar multimedia directamente.");
                return;
            }

            // Comprimir imagen pesada desde el navegador ANTES de subir para no saturar a Nginx/Meta
            const compressImage = async (inputFile) => {
                if (!inputFile.type.startsWith('image/') || inputFile.type === 'image/gif' || inputFile.size < 2.5 * 1024 * 1024) return inputFile;
                return new Promise((resolve) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        let w = img.width, h = img.height;
                        const maxDim = 1920; // Full HD es mÃƒÂ¡s que suficiente para Meta
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

            let modeIcon = mode === 'video' ? 'Ã°Å¸Å½Â¬' : mode === 'audio' ? 'Ã°Å¸Å½Âµ' : 'Ã°Å¸â€“Â¼Ã¯Â¸Â';

            // Dibujado de burbuja temporal "cargando" para liberar el UI general
            const scroll = document.getElementById('chatScroll');
            let loadingBubble = null;
            if (scroll) {
                loadingBubble = document.createElement('div');
                loadingBubble.className = "bubble bubble-bot lado-der";
                loadingBubble.setAttribute("data-temp", "true");
                loadingBubble.style.border = "1px dashed var(--accent-border)";
                loadingBubble.style.opacity = "0.7";
                loadingBubble.style.background = "rgba(0,0,0,0.2)";
                
                loadingBubble.innerHTML = `<div style="display:flex; align-items:center; gap:0.5rem; color:var(--text-main);">
                                              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin-anim"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>
                                              Subiendo ${modeIcon} (${(file.size/1024/1024).toFixed(1)}MB) en segundo plano...
                                           </div>`;
                scroll.appendChild(loadingBubble);
                scroll.scrollTop = scroll.scrollHeight;
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("mode", mode);

            try {
                // Sube el archivo de forma completamente asÃƒÂ­ncrona a nuestro servidor
                const res = await fetch('/api/admin/upload_media', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (data.ok && data.media_id) {
                    // Una vez subido con existo, SE MANDA EL MENSAJE AUTOMÃƒÂTICAMENTE a Meta
                    const textToSend = `[${mode}:${data.media_id}]`;
                    fetch('/api/admin/enviar_manual', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ wa_id: wa_id, texto: textToSend, reply_to_wamid: null, quick_reply_title: null })
                    });
                    
                    if (loadingBubble && document.body.contains(loadingBubble)) {
                        loadingBubble.innerHTML = `Ã¢Å“â€¦ ${modeIcon} Ã‚Â¡Procesado y enviado a Meta!`;
                        loadingBubble.style.border = "1px solid var(--primary-color)";
                        loadingBubble.style.opacity = "1";
                        setTimeout(() => { if (loadingBubble && loadingBubble.parentNode) loadingBubble.parentNode.removeChild(loadingBubble); }, 3000); 
                    } else {
                        showGlobalToast(`Ã¢Å“â€¦ ${modeIcon} Ã‚Â¡Video subido y enviado a +${wa_id} correctamente!`);
                    }
                } else {
                    if (loadingBubble && document.body.contains(loadingBubble)) {
                        loadingBubble.innerHTML = `Ã¢ÂÅ’ Error subiendo: ${data.error || "Desconocido"}`;
                        loadingBubble.style.border = "1px solid red";
                        setTimeout(() => { if (loadingBubble && loadingBubble.parentNode) loadingBubble.parentNode.removeChild(loadingBubble); }, 6000);
                    } else {
                        showGlobalToast(`Ã¢ÂÅ’ Falla al enviar ${modeIcon} a +${wa_id}: ${data.error || "Desconocido"}`);
                    }
                }
            } catch (e) {
                console.error(e);
                if (loadingBubble && document.body.contains(loadingBubble)) {
                    loadingBubble.innerHTML = `Ã¢ÂÅ’ Falla de fondo: ${e.message}`;
                    loadingBubble.style.border = "1px solid red";
                    setTimeout(() => { if (loadingBubble && loadingBubble.parentNode) loadingBubble.parentNode.removeChild(loadingBubble); }, 6000);
                } else {
                    showGlobalToast(`Ã¢ÂÅ’ FallÃƒÂ³ la subida de ${modeIcon} a +${wa_id} por error de red: ${e.message}`);
                }
            }
        };

        // NOTIFICACIONES GLOBALES INDESTRUCTIBLES
        window.showGlobalToast = function(msg) {
            const toast = document.createElement('div');
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.left = '50%';
            toast.style.transform = 'translateX(-50%)';
            toast.style.background = 'var(--primary-color)';
            toast.style.color = 'white';
            toast.style.padding = '1rem';
            toast.style.borderRadius = '8px';
            toast.style.boxShadow = '0 5px 15px rgba(0,0,0,0.5)';
            toast.style.zIndex = '999999';
            toast.style.fontWeight = '600';
            toast.style.maxWidth = '90%';
            toast.innerText = msg;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.5s';
                setTimeout(() => toast.remove(), 500);
            }, 6000);
        };

        // Pegar imagen directamente en el chat
        document.addEventListener('paste', function (e) {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let index in items) {
                const item = items[index];
                if (item.kind === 'file') {
                    const blob = item.getAsFile();
                    // Paste always defaults to 'imagen' type
                    uploadMedia(blob, 'imagen');
                }
            }
        });

        // Trigger de los inputs ocultos
        document.addEventListener('change', async function (e) {
            // Caso 1: Subida general (solo un archivo por click)
            if (e.target && e.target.id === 'hiddenFileInput') {
                const mode = e.target.getAttribute('data-mode') || 'imagen';
                if (e.target.files && e.target.files[0]) {
                    uploadMedia(e.target.files[0], mode);
                }
                e.target.value = ''; // Reset
            }
        });

        // Funcionalidad del Buscador Local y Nuevo Chat
        window.aplicarFiltroChats = function () {
            const input = document.getElementById('chatSearchInput');
            if (!input) return;
            const val = input.value.toLowerCase().trim();
            
            // Limit search scope to regular container so we don't accidentally hide our own search results
            const regularCont = document.getElementById('regularChatsContainer');
            const rows = regularCont ? regularCont.querySelectorAll('.chat-row') : document.querySelectorAll('.chat-row:not(#msgSearchResults .chat-row)');
            
            let isPhoneNum = /^[0-9+ ]+$/.test(val) && val.replace(/\D/g, '').length >= 9;

            rows.forEach(row => {
                const nameNode = row.querySelector('.chat-name');
                const name = nameNode ? nameNode.innerText.toLowerCase() : "";
                const phone = row.getAttribute('href') || "";
                if (name.includes(val) || phone.includes(val)) {
                    row.style.display = 'block';
                } else {
                    row.style.display = 'none';
                }
            });

            const btn = document.getElementById('btnNewChat');
            if (btn) {
                btn.style.display = isPhoneNum ? 'block' : 'none';
            }

            const searchCont = document.getElementById('msgSearchResults');
            if(searchCont) {
                if(val.length >= 3) {
                    if(window.searchTimeout) clearTimeout(window.searchTimeout);
                    window.searchTimeout = setTimeout(async () => {
                        try {
                            const res = await fetch(`/api/admin/buscar_mensajes?q=${encodeURIComponent(val)}`);
                            const data = await res.json();
                            if(data.ok && data.resultados && data.resultados.length > 0) {
                                let localChatsFound = 0; rows.forEach(r => {if(r.style.display==='block') localChatsFound++;});
                                if (localChatsFound === 0 && regularCont) regularCont.style.display = 'none';
                                
                                let html = `<div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem; padding-left:0.5rem; text-transform:uppercase; letter-spacing:1px;">Mensajes (${data.resultados.length})</div>`;
                                data.resultados.forEach(r => {
                                    r.matches.forEach(m => {
                                        let icon = m.role === 'assistant' ? 'Ã°Å¸Â¤â€“' : 'Ã°Å¸â€˜Â¤';
                                        html += `
                                        <a href="/inbox/${r.wa_id}" class="chat-row search-msg-row" style="display:block; text-decoration:none; background:var(--accent-bg); border-radius:8px; margin-bottom:0.5rem; padding:0.8rem; border:1px solid transparent; transition:border 0.2s;">
                                            <div style="font-weight:600; color:var(--text-main); font-size:0.9rem; margin-bottom:0.3rem; display:flex; justify-content:space-between;">
                                                <span>${r.nombre}</span>
                                            </div>
                                            <div style="color:var(--text-muted); font-size:0.8rem; line-height:1.4; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">
                                                <span style="opacity:0.6; margin-right:4px;">${icon}</span>${m.snippet.replace(new RegExp(val, "gi"), match => `<mark style="background:var(--primary-color); color:white; padding:0 2px; border-radius:2px;">${match}</mark>`)}
                                            </div>
                                        </a>`;
                                    });
                                });
                                searchCont.innerHTML = html;
                                searchCont.style.display = 'flex';
                            } else {
                                searchCont.style.display = 'none';
                                if(regularCont) regularCont.style.display = 'block';
                            }
                        } catch(e) { console.error('Global search error', e); }
                    }, 500); 
                } else {
                    if(window.searchTimeout) clearTimeout(window.searchTimeout);
                    searchCont.style.display = 'none';
                    if(regularCont) regularCont.style.display = 'block';
                }
            }
        };
        
        const searchInp = document.getElementById('chatSearchInput');
        if (searchInp) {
            const savedSearch = sessionStorage.getItem('chatSearchValue');
            if (savedSearch) {
                searchInp.value = savedSearch;
                // Wait for DOM to finish then apply
                setTimeout(() => { if(window.aplicarFiltroChats) window.aplicarFiltroChats(); }, 100);
            }
            
            searchInp.addEventListener('input', function(e) {
                sessionStorage.setItem('chatSearchValue', this.value);
                if(window.aplicarFiltroChats) window.aplicarFiltroChats();
            });
        }

        const chatsContainerDiv = document.getElementById('regularChatsContainer');
        if (chatsContainerDiv) {
            const applyScroll = () => {
                const s = sessionStorage.getItem('chatListScrollTop');
                if (s) chatsContainerDiv.scrollTop = parseInt(s);
            };
            
            // Apply immediately, and firmly a few times to beat browser rendering or filter passes
            applyScroll();
            setTimeout(applyScroll, 50);
            setTimeout(applyScroll, 150);
            setTimeout(applyScroll, 300);

            // Record cleanly using event listener, throttled/debounced implicitly? 
            chatsContainerDiv.addEventListener('scroll', function() {
                sessionStorage.setItem('chatListScrollTop', this.scrollTop);
            });

            // Adicionalmente, asegurar que si se hace clic en un chat, se guarde justo ese instante
            const chatLinks = chatsContainerDiv.querySelectorAll('.chat-row');
            chatLinks.forEach(link => {
                link.addEventListener('click', () => {
                    sessionStorage.setItem('chatListScrollTop', chatsContainerDiv.scrollTop);
                });
            });
        }


        function iniciarNuevoChat() {
            let val = document.getElementById('chatSearchInput').value.trim();
            val = val.replace(/\D/g, ''); // purgar caracteres no numÃƒÂ©ricos
            if (val.length < 9) return alert("NÃƒÂºmero muy corto");
            if (!val.startsWith("51")) val = "51" + val;
            window.location.href = `/inbox/${val}`;
        }

        // EMOJI PICKER HOOK - Global event delegation
        document.addEventListener('emoji-click', event => {
            const input = document.getElementById('manualMsgInput');
            if (input) {
                input.value += event.detail.unicode;
                input.focus();
            }
        });

        // CERRAR MENÃƒÅ¡S FLOTANTES AL HACER CLICK AFUERA
        document.addEventListener("click", function (e) {
            const combinedEmojiMenu = document.getElementById("combinedEmojiMenu");
            if (combinedEmojiMenu && !e.target.closest('#combinedEmojiMenu') && !e.target.closest('button[title="Emojis y Stickers"]')) {
                combinedEmojiMenu.style.display = "none";
            }
            const cameraMenu = document.getElementById("cameraMenu");
            if (cameraMenu && !e.target.closest('#cameraMenu') && !e.target.closest('#btnRightPhoto')) {
                cameraMenu.style.display = "none";
            }

            const attachMenu = document.getElementById("attachMenu");
            if (attachMenu && !e.target.closest('#attachMenu') && !e.target.closest('button[title="Adjuntar"]')) {
                attachMenu.style.display = "none";
            }

            const templateMenu = document.getElementById("templateMenu");
            if (templateMenu && !e.target.closest('#templateMenu') && !e.target.closest('button[title="Plantillas (24h)"]')) {
                templateMenu.style.display = "none";
            }

            const chatLabelMenu = document.getElementById("chatLabelMenu");
            if (chatLabelMenu && !e.target.closest('#chatLabelMenu') && !e.target.closest('button[title="Etiquetas del Chat"]')) {
                chatLabelMenu.style.display = "none";
            }

            const filterMenu = document.getElementById('inboxFilterMenu');
            if (filterMenu && !e.target.closest('#inboxFilterMenu') && !e.target.closest('button') && !e.target.closest('svg')) {
                filterMenu.style.display = 'none';
            }
        });

        // ================= PLANTILLAS LOGIC =================
        async function cargarPlantillas() {
            const list = document.getElementById("templateList");
            if (!list) return;
            list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Cargando...</div>`;
            try {
                const res = await fetch("/api/admin/templates/list");
                const data = await res.json();
                if (data.ok) {
                    list.innerHTML = "";
                    if (data.plantillas.length === 0) {
                        list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Sin plantillas. Apreta (+) para aÃƒÂ±adir.</div>`;
                    } else {
                        data.plantillas.forEach(p => {
                            const btn = document.createElement("div");
                            btn.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding:0.5rem; background:var(--bg-main); border-radius:6px; font-size:0.85rem;";

                            const sendBtn = document.createElement("button");
                            sendBtn.type = "button";
                            sendBtn.innerText = p.name;
                            sendBtn.style.cssText = "background:none; border:none; text-align:left; cursor:pointer; color:var(--text-main); font-weight:500; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;";
                            sendBtn.onclick = () => enviarPlantillaLoc(p.name, p.language);

                            const delBtn = document.createElement("button");
                            delBtn.type = "button";
                            delBtn.innerText = "Ãƒâ€”";
                            delBtn.style.cssText = "background:none; border:none; cursor:pointer; color:#ef4444; font-size:1.1rem; padding:0 0.2rem;";
                            delBtn.onclick = () => eliminarPlantilla(p.name);

                            btn.appendChild(sendBtn);
                            btn.appendChild(delBtn);
                            list.appendChild(btn);
                        });
                    }
                }
            } catch (e) {
                list.innerHTML = `<div style="font-size:0.8rem; color:red; padding:0.5rem; text-align:center;">Error al cargar</div>`;
            }
        }

        async function crearPlantilla() {
            const name = prompt("Escribe el NOMBRE EXACTO de la plantilla en Meta (ej: hola_cliente)");
            if (!name) return;
            const lang = prompt("Esribe el cÃƒÂ³digo de idioma (ej: es, es_PE). Si no sabes, pon 'es'") || "es";
            try {
                const res = await fetch("/api/admin/templates/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: name.trim(), language: lang.trim() })
                });
                if (res.ok) cargarPlantillas();
            } catch (e) {
                alert("Error guardando plantilla");
            }
        }

        async function eliminarPlantilla(name) {
            if (!confirm(`Ã‚Â¿Borrar la plantilla '${name}' de tu lista local?`)) return;
            try {
                const res = await fetch("/api/admin/templates/delete", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: name })
                });
                if (res.ok) cargarPlantillas();
            } catch (e) {
                alert("Error eliminando plantilla");
            }
        }

        async function enviarPlantillaLoc(name, lang) {
            const wa_id = location.pathname.split("/").pop(); // Obtiene el NÃ‚Â° de la URL
            if (!wa_id || isNaN(wa_id)) return alert("No hay un chat vÃƒÂ¡lido seleccionado.");

            if (!confirm(`Se le enviarÃƒÂ¡ la plantilla '${name}' al nÃƒÂºmero +${wa_id}. Ã‚Â¿Deseas continuar?`)) return;
            const tMenu = document.getElementById("templateMenu");
            if(tMenu) tMenu.style.display = "none";

            try {
                const res = await fetch("/api/admin/enviar_plantilla", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ wa_id: wa_id, template_name: name, language_code: lang })
                });
                const data = await res.json();
                if (data.ok) {
                    // Cargar el chat inmediatamente para ver la burbuja
                    window.location.reload();
                } else {
                    alert("Ã¢ÂÅ’ Error: " + data.error);
                }
            } catch (e) {
                alert("Falla de conectividad");
            }
        }

        // ================= ETIQUETAS (LABELS) LOGIC =================
        function crearGlobalLabel() {
            // Abrir el modal en lugar de prompt()
            const modal = document.getElementById("createLabelModal");
            if (modal) {
                document.getElementById("newLabelName").value = "";
                // Reset a color por defecto
                const firstColor = document.getElementById("color-grid-container").querySelector('.color-option');
                if (firstColor) seleccionarColorEtiqueta("#717f7f", firstColor);
                modal.style.display = "flex";
            }
        }

        async function guardarNuevaEtiquetaModal() {
            const nameInput = document.getElementById("newLabelName");
            if (!nameInput) return;
            const name = nameInput.value.trim();
            if (!name) return alert("Por favor, ingresa un nombre para la etiqueta.");

            const color = document.getElementById("newLabelColor").value || "#94a3b8";
            const id = 'lbl_' + Date.now();

            try {
                const res = await fetch("/api/admin/labels/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id: id, name: name, color: color })
                });
                if (res.ok) {
                    document.getElementById("createLabelModal").style.display = "none";
                    cargarChatLabels();
                } else {
                    alert("Error guardando etiqueta (Respuesta del servidor).");
                }
            } catch (e) {
                alert("Error guardando etiqueta (Conectividad).");
            }
        }

        async function eliminarGlobalLabel(id, name, event) {
            event.stopPropagation();
            if (!confirm(`Ã‚Â¿Borrar la etiqueta global '${name}' de todo el sistema? (Se eliminarÃƒÂ¡ de todos los chats asignados).`)) return;
            try {
                const res = await fetch("/api/admin/labels/delete", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id: id })
                });
                if (res.ok) window.location.reload();
            } catch (e) {
                alert("Error eliminando etiqueta");
            }
        }

        async function cargarChatLabels() {
            const list = document.getElementById("chatLabelList");
            if (!list) return;
            list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Cargando...</div>`;

            try {
                const res = await fetch("/api/admin/labels/list");
                const data = await res.json();

                if (data.ok) {
                    list.innerHTML = "";
                    if (data.labels.length === 0) {
                        list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem; text-align:center;">Sin etiquetas. Apreta (+) para aÃƒÂ±adir.</div>`;
                    } else {
                        data.labels.forEach(lbl => {
                            const btn = document.createElement("div");
                            btn.style.cssText = "display:flex; justify-content:space-between; align-items:center; padding:0.4rem; background:var(--bg-main); border-radius:6px; font-size:0.85rem; cursor:pointer;";
                            btn.onclick = () => alternarChatLabel(lbl.id);

                            const colorDot = document.createElement("div");
                            colorDot.style.cssText = `width:12px; height:12px; border-radius:50%; background:${lbl.color}; margin-right:0.5rem;`;

                            const nameSpan = document.createElement("span");
                            nameSpan.innerText = lbl.name;
                            nameSpan.style.cssText = "flex:1; color:var(--text-main); font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;";

                            const delBtn = document.createElement("button");
                            delBtn.type = "button";
                            delBtn.innerText = "Ãƒâ€”";
                            delBtn.style.cssText = "background:none; border:none; cursor:pointer; color:var(--text-muted); font-size:1.1rem; padding:0 0.2rem;";
                            delBtn.onclick = (e) => eliminarGlobalLabel(lbl.id, lbl.name, e);

                            btn.appendChild(colorDot);
                            btn.appendChild(nameSpan);
                            btn.appendChild(delBtn);
                            list.appendChild(btn);
                        });
                    }
                }
            } catch (e) {
                list.innerHTML = `<div style="font-size:0.8rem; color:red; padding:0.5rem; text-align:center;">Error al cargar</div>`;
            }
        }

        async function alternarChatLabel(lbl_id) {
            const wa_id = location.pathname.split("/").pop(); // Obtiene el NÃ‚Â° de la URL
            if (!wa_id || isNaN(wa_id)) return alert("No hay un chat vÃƒÂ¡lido seleccionado.");

            try {
                const res = await fetch(`/api/admin/chats/labels/toggle`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ wa_id: wa_id, label_id: lbl_id, action: "toggle" })
                });

                const data = await res.json();
                if (data.ok) {
                    window.location.reload();
                } else {
                    alert("Error: " + data.error);
                }
            } catch (e) {
                alert("Error de conexiÃƒÂ³n al alternar etiqueta.");
            }
        }


    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            // Auto seleccionar el mensaje al que dimos click derecho
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks during selection
        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true); // Use capture phase!

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            // Load frequent chats
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un n\u00famero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert(\u00A1Enviado! Mensajes enviados a  + data.count +  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error:  + (data.error || 'Algo sali\u00F3 mal'));
                }
            } catch(e) {
                alert("Error de red enviando petici\u00F3n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

                        const predefinedColors = ["#ef4444", "#f97316", "#f59e0b", "#eab308", "#84cc16", "#22c55e", "#10b981", "#14b8a6", "#06b6d4", "#0ea5e9", "#717f7f", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899", "#f43f5e", "#64748b", "#78716c", "#52525b"];
                        let colorsHtml = '';
                        predefinedColors.forEach((color, idx) => {
                            const isSelected = idx === 10 ? 'box-shadow: 0 0 0 2px var(--bg-main), 0 0 0 4px ' + color + ';' : 'border:2px solid transparent;';
                            colorsHtml += `<button type="button" class="color-option" style="width:100%; aspect-ratio:1; border-radius:50%; background:${color}; cursor:pointer; ${isSelected} transition:transform 0.1s;" onclick="seleccionarColorEtiqueta('${color}', this)"></button>`;
                        });
                        document.write(colorsHtml);

                        function seleccionarColorEtiqueta(color, element) {
                            document.getElementById("newLabelColor").value = color;
                            const options = document.querySelectorAll('.color-option');
                            options.forEach(opt => {
                                opt.style.boxShadow = 'none';
                                opt.style.border = '2px solid transparent';
                            });
                            element.style.boxShadow = `0 0 0 2px var(--bg-main), 0 0 0 4px ${color}`;
                        }
                    
        
        // Intercept clicks on other chats if a sequence is sending
        document.addEventListener('click', async function(e) {
            const chatRow = e.target.closest('.chat-row');
            if (chatRow && window.isSendingSequence) {
                e.preventDefault();
                const url = chatRow.href;
                
                // Soft Navigation (PJAX style)
                window.history.pushState(null, '', url);
                document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
                chatRow.classList.add('active-row');
                
                const viewer = document.querySelector('.chat-viewer-panel');
                if (viewer) {
                    viewer.innerHTML = '<div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);"><h3>Cargando chat en segundo plano...</h3></div>';
                    try {
                        const response = await fetch(url);
                        const html = await response.text();
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newViewer = doc.querySelector('.chat-viewer-panel');
                        if (newViewer) {
                            viewer.innerHTML = newViewer.innerHTML;
                        }
                    } catch(err) {
                        window.location.href = url; // Fallback
                    }
                }
            }
        });

        // Smart ESC to exit chat without interrupting sequence

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    
                    // Soft Virtual Exit to instantly clear chat UI without reloading
                    window.history.replaceState(null, '', `/inbox?tab=${tab}`);
                    
                    document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
                    
                    const viewer = document.querySelector('.chat-viewer-panel');
                    if (viewer) {
                        viewer.innerHTML = `
                        <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
                            <h3>Bandeja de Entrada</h3>
                            <p style="font-size:0.9rem; max-width:400px; text-align:center;">Selecciona una conversaciÃƒÂ³n para empezar o continuar chateando.</p>
                        </div>`;
                    }
                }
            }
        });

// FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            // Auto seleccionar el mensaje al que dimos click derecho
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks during selection
        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true); // Use capture phase!

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            // Load frequent chats
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un n\u00famero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert(\u00A1Enviado! Mensajes enviados a  + data.count +  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error:  + (data.error || 'Algo sali\u00F3 mal'));
                }
            } catch(e) {
                alert("Error de red enviando petici\u00F3n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

        document.addEventListener('click', function(e) {
            if (e.target.tagName && e.target.tagName.toLowerCase() === 'img') {
                const alt = e.target.getAttribute('alt');
                if (alt && alt.startsWith('Imagen')) {
                    const lb = document.getElementById('imageLightbox');
                    const lbImg = document.getElementById('lightboxImg');
                    if (lb && lbImg) {
                        lbImg.src = e.target.src;
                        lb.style.display = 'flex';
                    }
                }
            }
        });
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            // Auto seleccionar el mensaje al que dimos click derecho
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks during selection
        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true); // Use capture phase!

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            // Load frequent chats
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un n\u00famero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert(\u00A1Enviado! Mensajes enviados a  + data.count +  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error:  + (data.error || 'Algo sali\u00F3 mal'));
                }
            } catch(e) {
                alert("Error de red enviando petici\u00F3n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

        let targetPhoneCtx = "";
        function abrirCtxTelefono(e, phone) {
            e.preventDefault();
            e.stopPropagation();
            targetPhoneCtx = phone;

            let menu = document.getElementById('phoneContextMenu');
            document.getElementById('ctxPhoneTitle').innerText = "+" + phone;

            menu.style.display = 'block';
            let x = e.clientX;
            let y = e.clientY;
            if (x + menu.offsetWidth > window.innerWidth) x = window.innerWidth - menu.offsetWidth - 10;
            if (y + menu.offsetHeight > window.innerHeight) y = window.innerHeight - menu.offsetHeight - 10;
            menu.style.left = x + 'px';
            menu.style.top = y + 'px';
        }

        document.getElementById("ctxPhoneChat").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            const wa_id = targetPhoneCtx.replace(/\D/g, '');
            if(wa_id.length > 6) {
                let final_wa_id = wa_id;
                try {
                    const res = await fetch('/api/admin/chat/init', { method: 'POST', body: JSON.stringify({wa_id}), headers:{'Content-Type':'application/json'} });
                    if(res.ok) {
                        const data = await res.json();
                        if(data.wa_id) final_wa_id = data.wa_id;
                    }
                } catch(e) {}
                window.location.href = "/inbox/" + final_wa_id;
            }
        });

        document.getElementById("ctxPhoneCopy").addEventListener('click', async () => {
            document.getElementById('phoneContextMenu').style.display = 'none';
            try {
                await navigator.clipboard.writeText("+" + targetPhoneCtx.replace(/\D/g, ''));
            } catch(e) {}
        });

        document.addEventListener('click', () => {
            const m = document.getElementById('phoneContextMenu');
            if(m) m.style.display = 'none';
        });
    
        document.body.addEventListener('click', async (e) => {
            const btnCancel = e.target.closest('#btnCancelAudio');
            if (btnCancel && typeof mediaRecorder !== 'undefined' && mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.canceled = true; // sets custom flag so the 'stop' event ignores it
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(t => t.stop()); // close microphone
                
                const btnRecord = document.getElementById('btnRecordAudio');
                if (btnRecord) {
                    isRecording = false;
                    window._isAudioRecording = false;
                    if(window.toggleSendMicButton) window.toggleSendMicButton();
                    btnRecord.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>`;
                    btnRecord.style.color = "var(--text-main)";
                }
                btnCancel.style.display = 'none';
            }
        });
    
        

        
        // Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ Panel de Info de Mensaje Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
        function formatTsUnix(ts) {
            if (!ts) return 'Ã¢â‚¬â€';
            const d = new Date(parseInt(ts) * 1000);
            return d.toLocaleString('es-PE', {
                hour: '2-digit', minute: '2-digit',
                day: '2-digit', month: 'short', year: 'numeric'
            });
        }

        function openMsgInfoPanel(bubble) {
            const sentBy = bubble.dataset.sentBy || 'Ã¢â‚¬â€';
            const ts = bubble.dataset.ts || '';
            const deliveredTs = bubble.dataset.deliveredTs || '';
            const readTs = bubble.dataset.readTs || '';
            const qrTitle = bubble.dataset.quickReply || '';
            // Get text without meta (timestamp/ticks)
            const clone = bubble.cloneNode(true);
            const metaEl = clone.querySelector('.msg-meta');
            if (metaEl) metaEl.remove();
            const preview = clone.innerText.trim().slice(0, 200);

            document.getElementById('info-preview-text').textContent = preview || 'Ã¢â‚¬â€';
            document.getElementById('info-sent-by').textContent = sentBy;
            
            // Handle QR title display
            const qrRow = document.getElementById('info-row-qr');
            if (qrTitle) {
                document.getElementById('info-qr-title').textContent = qrTitle;
                qrRow.style.display = 'flex';
            } else {
                qrRow.style.display = 'none';
            }
            document.getElementById('info-sent-ts').textContent = formatTsUnix(ts);
            document.getElementById('info-delivered-ts').textContent = deliveredTs ? formatTsUnix(deliveredTs) : 'Ã¢â‚¬â€';
            document.getElementById('info-read-ts').textContent = readTs ? formatTsUnix(readTs) : 'Ã¢â‚¬â€';

            document.getElementById('msg-info-panel').classList.add('open');
        }

        function closeMsgInfoPanel() {
            document.getElementById('msg-info-panel').classList.remove('open');
        }

        const ctxInfoBtn = document.getElementById('ctxMsgInfo');
        if (ctxInfoBtn) {
            ctxInfoBtn.addEventListener('click', function() {
                document.getElementById('bubbleContextMenu').style.display = 'none';
                if (ctxTargetBubble) openMsgInfoPanel(ctxTargetBubble);
            });
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeMsgInfoPanel();
        });

        // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            // Auto seleccionar el mensaje al que dimos click derecho
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks during selection
        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true); // Use capture phase!

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            // Load frequent chats
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un n\u00famero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert(\u00A1Enviado! Mensajes enviados a  + data.count +  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error:  + (data.error || 'Algo sali\u00F3 mal'));
                }
            } catch(e) {
                alert("Error de red enviando petici\u00F3n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    // FORWARD LOGIC
        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            <label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">
                                <input type="checkbox" class="frequent-chat-checkbox" value="+chat.wa_id+">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;">+chat.nombre+</span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;">+chat.wa_id+</span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

        let isForwardMode = false;
        let forwardSelectedWamids = [];
        let sourceWaId = "";

        document.getElementById("ctxForward").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            let q = window.location.search;
            let currentParams = new URLSearchParams(q);
            sourceWaId = currentParams.get('wa_id');
            if(!sourceWaId) return alert("Debes estar en un chat activo para reenviar.");
            
            isForwardMode = true;
            forwardSelectedWamids = [];
            
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        document.addEventListener('click', function(e) {
            if (isForwardMode) {
                let bubble = e.target.closest('.bubble');
                if (bubble) {
                    e.preventDefault();
                    e.stopPropagation();
                    let wamid = bubble.getAttribute('data-wamid');
                    if (wamid) {
                        if (forwardSelectedWamids.includes(wamid)) {
                            forwardSelectedWamids = forwardSelectedWamids.filter(x => x !== wamid);
                            bubble.classList.remove('forward-selected');
                        } else {
                            forwardSelectedWamids.push(wamid);
                            bubble.classList.add('forward-selected');
                        }
                        updateForwardUI();
                    }
                    return;
                }
            }
        }, true);

        function updateForwardUI() {
            document.getElementById('forwardCount').innerText = forwardSelectedWamids.length;
            let btn = document.getElementById('forwardExecuteBtn');
            if(forwardSelectedWamids.length > 0) {
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            } else {
                btn.style.opacity = '0.5';
                btn.style.pointerEvents = 'none';
            }
        }

        function cancelForwardMode() {
            isForwardMode = false;
            forwardSelectedWamids = [];
            document.getElementById('forwardTopBar').style.display = 'none';
            document.querySelectorAll('.bubble.forward-selected').forEach(el => el.classList.remove('forward-selected'));
            document.getElementById('forwardManualNumbers').value = '';
            closeForwardModal();
        }

        async function openForwardModal() {
            if(forwardSelectedWamids.length === 0) return;
            document.getElementById('forwardTargetModal').style.display = 'flex';
            
            try {
                const res = await fetch('/api/frequent_chats');
                if(res.ok) {
                    const data = await res.json();
                    const container = document.getElementById('frequentChatsContainer');
                    if(data.chats && data.chats.length > 0) {
                        container.innerHTML = data.chats.map(chat => 
                            '<label style="display:flex; align-items:center; gap:0.8rem; padding:0.6rem; border-radius:8px; background:var(--bg-main); border:1px solid var(--accent-border); cursor:pointer;">' +
                                '<input type="checkbox" class="frequent-chat-checkbox" value="' + chat.wa_id + '">' +
                                '<div style="display:flex; flex-direction:column;">' +
                                    '<span style="color:var(--text-main); font-weight:600;">' + chat.nombre + '</span>' +
                                    '<span style="color:var(--text-muted); font-size:0.8rem;">' + chat.wa_id + '</span>' +
                                '</div>' +
                            '</label>'
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) { }
        }

        function closeForwardModal() {
            document.getElementById('forwardTargetModal').style.display = 'none';
        }

        async function executeForwarding() {
            let manualInput = document.getElementById('forwardManualNumbers').value.trim();
            let targets = [];
            
            if(manualInput) {
                targets = manualInput.split(' ').map(s => s.trim()).filter(s => s);
            }
            
            document.querySelectorAll('.frequent-chat-checkbox:checked').forEach(chk => {
                if(!targets.includes(chk.value)) targets.push(chk.value);
            });
            
            if(targets.length === 0) {
                return alert("Selecciona al menos un chat o ingresa un nÃºmero.");
            }
            
            let btn = document.getElementById('btnConfirmForward');
            let prevText = btn.innerText;
            btn.innerText = "Enviando...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            try {
                const res = await fetch('/api/forward_messages', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        source_wa_id: sourceWaId,
                        wamids: forwardSelectedWamids,
                        targets: targets
                    })
                });
                
                const data = await res.json();
                if(res.ok && data.ok) {
                    alert('Â¡Enviado! Mensajes enviados a ' + data.count + ' destino(s).');
                    cancelForwardMode();
                } else {
                    alert('Error: ' + (data.error || 'Algo saliÃ³ mal'));
                }
            } catch(e) {
                alert("Error de red enviando peticiÃ³n.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
    

