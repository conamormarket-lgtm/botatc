
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
    

