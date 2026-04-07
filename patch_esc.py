import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

old_esc = '''// Pure ESC to exit chat
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    window.location.href = `/inbox?tab=${tab}`;
                }
            }
        });'''

new_esc = '''// Smart ESC to exit chat without interrupting sequence
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    
                    if (window.isSendingSequence) {
                        // Soft Virtual Exit to keep sequence sending in background
                        window.history.pushState(null, '', `/inbox?tab=${tab}`);
                        
                        document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
                        
                        const viewer = document.querySelector('.chat-viewer-panel');
                        if (viewer) {
                            viewer.innerHTML = `
                            <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);">
                                <h3>Bandeja de Entrada</h3>
                                <p style="font-size:0.9rem; max-width:400px;">Selecciona una conversación para empezar o continuar chateando.</p>
                            </div>`;
                        }
                    } else {
                        // Normal Hard Exit
                        window.location.href = `/inbox?tab=${tab}`;
                    }
                }
            }
        });'''

if 'Smart ESC' not in text:
    text = text.replace(old_esc, new_esc)
    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("ESC logic updated")
else:
    print("Already updated")
