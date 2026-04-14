import sys

with open('inbox.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add ctxForward into context menu
menu_injection = """
        <div class="ctx-item" id="ctxForward" style="padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; border-bottom:1px solid var(--accent-border); color:var(--text-main); display:flex; align-items:center; gap:0.5rem; transition:background 0.2s;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12H3"/><path d="M21 12l-8-8"/><path d="M21 12l-8 8"/></svg>
            Reenviar
        </div>
        <div class="ctx-item" id="ctxReply"
"""
content = content.replace('<div class="ctx-item" id="ctxReply"', menu_injection)

# 2. Add Topbar and Modal UI to the body
ui_injection = """
    <!-- FORWARD TOP BAR -->
    <div id="forwardTopBar" style="display:none; position:fixed; top:0; left:0; width:100%; height:60px; background:var(--bg-main); border-bottom:1px solid var(--accent-border); z-index:9000; align-items:center; justify-content:space-between; padding:0 2rem; box-sizing:border-box; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
        <div style="display:flex; align-items:center; gap:1rem;">
            <button onclick="cancelForwardMode()" style="background:transparent; border:none; color:var(--text-main); cursor:pointer; font-size:1.5rem; padding:0; display:flex;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
            <span style="color:var(--text-main); font-weight:600; font-family:var(--font-heading);"><span id="forwardCount">0</span> seleccionados</span>
        </div>
        <button id="forwardExecuteBtn" onclick="openForwardModal()" style="background:var(--primary-color); color:#fff; border:none; padding:0.5rem 1.5rem; border-radius:30px; font-weight:600; cursor:pointer; opacity:0.5; pointer-events:none; display:flex; align-items:center; gap:0.5rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12H3"/><path d="M21 12l-8-8"/><path d="M21 12l-8 8"/></svg>
            Reenviar
        </button>
    </div>

    <!-- FORWARD MODAL -->
    <div id="forwardTargetModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:10000; align-items:center; justify-content:center;">
        <div style="background:var(--bg-main); border-radius:12px; border:1px solid var(--accent-border); width:400px; max-width:90vw; padding:1.5rem; display:flex; flex-direction:column; gap:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0; color:var(--text-main); font-family:var(--font-heading);">Reenviar mensajes a...</h3>
                <button onclick="closeForwardModal()" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">&times;</button>
            </div>
            
            <div>
                <label style="color:var(--text-muted); font-size:0.8rem; margin-bottom:0.3rem; display:block;">Múltiples números (separados por espacio)</label>
                <input type="text" id="forwardManualNumbers" placeholder="Ej: 51987654321 51999888777" style="width:100%; padding:0.8rem; border-radius:8px; border:1px solid var(--accent-border); background:var(--accent-bg); color:var(--text-main); font-family:var(--font-main);">
            </div>
            
            <div>
                <label style="color:var(--text-muted); font-size:0.8rem; margin-bottom:0.3rem; display:block;">Chats Frecuentes</label>
                <div id="frequentChatsContainer" style="display:flex; flex-direction:column; gap:0.5rem; max-height:200px; overflow-y:auto;">
                    <!-- Cargado por JS -->
                    <div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">Cargando...</div>
                </div>
            </div>
            
            <button id="btnConfirmForward" onclick="executeForwarding()" style="width:100%; background:var(--primary-color); color:#fff; border:none; padding:1rem; border-radius:8px; font-weight:600; cursor:pointer; font-size:1rem; margin-top:0.5rem;">Enviar Mensajes</button>
        </div>
    </div>
"""
content = content.replace("</body>", ui_injection + "\n</body>")

css_injection = """
        .bubble.forward-selected {
            background-color: var(--accent-bg) !important;
            border: 2px solid var(--primary-color) !important;
            opacity: 0.8;
            transform: scale(0.98);
        }
"""
content = content.replace("</style>", css_injection + "\n    </style>")

js_injection = """
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
            
            // Auto seleccionar el mensaje en el que hicimos click
            if(ctxTargetWamid) {
                forwardSelectedWamids.push(ctxTargetWamid);
                if(ctxTargetBubble) ctxTargetBubble.classList.add('forward-selected');
            }
            
            updateForwardUI();
            document.getElementById('forwardTopBar').style.display = 'flex';
        });

        // Intercept bubble clicks and prevent default when in forward mode
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
        }, true); // Use capture phase to stop other handlers!

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
            document.getElementById('frequentChatsContainer').innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">Cargando...</div>';
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
                                <input type="checkbox" class="frequent-chat-checkbox" value="">
                                <div style="display:flex; flex-direction:column;">
                                    <span style="color:var(--text-main); font-weight:600;"></span>
                                    <span style="color:var(--text-muted); font-size:0.8rem;"></span>
                                </div>
                            </label>
                        ).join('');
                    } else {
                        container.innerHTML = '<div style="color:var(--text-muted); font-size:0.9rem; text-align:center; padding:1rem;">No hay chats frecuentes.</div>';
                    }
                }
            } catch(e) {
                console.error("Error loading frequent chats", e);
            }
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
                return alert("Selecciona al menos un chat o ingresa un número de teléfono.");
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
                    alert(¡Enviado! Mensajes enviados a  destino(s).);
                    cancelForwardMode();
                } else {
                    alert(Error: );
                }
            } catch(e) {
                alert("Error de red enviando petición.");
            }
            
            btn.innerText = prevText;
            btn.disabled = false;
            btn.style.opacity = "1";
            closeForwardModal();
        }
"""
content = content.replace("</script>", js_injection + "\n</script>", 1)

# Write back
with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("INJECTION COMPLETE")
