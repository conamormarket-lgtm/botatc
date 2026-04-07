import os

ibx = open('inbox.html', 'r', encoding='utf-8').read()

# 1. Add .skeleton CSS
skeleton_css = '''
        .skeleton {
            background: linear-gradient(90deg, var(--accent-bg) 25%, var(--accent-border) 50%, var(--accent-bg) 75%);
            background-size: 400% 100%;
            animation: skeleton-loading 1.5s infinite linear;
        }
        @keyframes skeleton-loading {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }
'''
if '.skeleton {' not in ibx:
    ibx = ibx.replace('</style>', skeleton_css + '\n</style>')

# 2. Add Esc and Skeleton logic
logic_js = '''
        // --- NAVEGACIÓN Y SKELETONS ---
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                let closedModal = false;
                ['qrCreateModal', 'rightSidebar', 'emojiMenu', 'attachMenu', 'inboxFilterMenu', 'bubbleContextMenu'].forEach(id => {
                    const el = document.getElementById(id);
                    if(el && el.style.display !== 'none' && el.style.display !== '') {
                        el.style.display = 'none';
                        closedModal = true;
                    }
                });
                
                // Si no se cerró ningún menú y estamos dentro de un chat, ir al inicio
                if(!closedModal && window.location.pathname.match(/^\/inbox\/.+/)) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    window.location.href = `/inbox?tab=${tab}`;
                }
            }
        });

        document.addEventListener('click', function(e) {
            const chatRow = e.target.closest('a.chat-row');
            if(chatRow) {
                const chatViewer = document.querySelector('.chat-viewer-panel');
                if(chatViewer) {
                    // Muestra el skeleton layout simulando un chat mientras el navegador navega a la URL
                    chatViewer.innerHTML = `
                    <div style="flex:1; display:flex; flex-direction:column; min-width:0; background:var(--bg-main);">
                        <!-- Header Skeleton -->
                        <div style="padding:1.5rem;border-bottom:1px solid var(--accent-border);display:flex;align-items:center;background:var(--bg-main);gap:1rem;">
                            <div class="skeleton" style="width:45px; height:45px; border-radius:50%;"></div>
                            <div style="display:flex; flex-direction:column; gap:0.4rem; flex:1;">
                                <div class="skeleton" style="width:150px; height:16px; border-radius:4px;"></div>
                                <div class="skeleton" style="width:80px; height:12px; border-radius:4px;"></div>
                            </div>
                        </div>
                        
                        <!-- Messages Skeleton -->
                        <div style="flex:1; padding:2rem; display:flex; flex-direction:column; gap:1.2rem;">
                            <div class="skeleton" style="width:70%; max-width:300px; height:60px; border-radius:12px 12px 12px 0;"></div>
                            <div class="skeleton" style="width:85%; max-width:400px; height:80px; border-radius:12px 12px 12px 0;"></div>
                            <div class="skeleton" style="width:60%; max-width:250px; height:50px; border-radius:12px 12px 0 12px; align-self:flex-end;"></div>
                            <div class="skeleton" style="width:40%; max-width:200px; height:50px; border-radius:12px 12px 12px 0;"></div>
                        </div>
                        
                        <!-- Input Skeleton -->
                        <div style="padding:1rem 1.5rem;border-top:1px solid var(--accent-border);background:var(--accent-bg); display:flex; gap:0.8rem; align-items:center;">
                            <div class="skeleton" style="width:44px; height:44px; border-radius:50%;"></div>
                            <div class="skeleton" style="width:44px; height:44px; border-radius:50%;"></div>
                            <div class="skeleton" style="flex:1; height:44px; border-radius:12px;"></div>
                            <div class="skeleton" style="width:80px; height:44px; border-radius:12px;"></div>
                        </div>
                    </div>
                    `;
                }
            }
        });
'''
if 'NAVEGACIÓN Y SKELETONS' not in ibx:
    ibx = ibx.replace('</script>', logic_js + '\n</script>')

open('inbox.html', 'w', encoding='utf-8').write(ibx)

print("Patch inbox logic successful")
