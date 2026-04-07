import re

ibx = open('inbox.html', 'r', encoding='utf-8').read()

# 1. Update from patch_emoji
old_toggle_menu = '''        window.toggleStickersMenu = async function() {
            const drawer = document.getElementById('stickersDrawer');
            if(!drawer) return;
            
            if (drawer.style.display === 'none' || drawer.style.display === '') {
                drawer.style.display = 'block';
                const grid = document.getElementById('stickersGrid');
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5;">Cargando...</div>';
                try {
                    const res = await fetch('/api/stickers');
                    const data = await res.json();
                    if(data.stickers && data.stickers.length > 0) {
                        grid.innerHTML = data.stickers.map(s => 
                            `<img src="/static/stickers/${s}" style="width:80px; height:80px; object-fit:contain; cursor:pointer; padding:5px; border-radius:8px; border:2px solid transparent; transition:border 0.2s;" onmouseover="this.style.border='2px solid var(--primary-color)'" onmouseout="this.style.border='2px solid transparent'" onclick="insertStickerLocal('${s}')" title="${s}">`
                        ).join('');
                    } else {
                        grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5;">Aún no has subido stickers.<br>Copia archivos .webp en la carpeta <pre style="display:inline;background:var(--accent-bg);padding:3px;border-radius:4px;">static/stickers</pre> de tu servidor.</div>';
                    }
                } catch(e) { grid.innerHTML = '<div style="grid-column: 1/-1; padding:2rem; color:var(--danger-color);">Error cargando.</div>'; }
                
                // Scroll to make drawer visible
                drawer.scrollIntoView({ behavior: "smooth" });
            } else {
                drawer.style.display = 'none';
            }
        };'''

new_toggle_menu = '''        window.cargarStickers = async function() {
            const grid = document.getElementById('stickersGrid');
            if(!grid) return;
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5;">Cargando...</div>';
            try {
                const res = await fetch('/api/stickers');
                const data = await res.json();
                if(data.stickers && data.stickers.length > 0) {
                    grid.innerHTML = data.stickers.map(s => 
                        `<img src="/static/stickers/${s}" style="width:70px; height:70px; object-fit:contain; cursor:pointer; padding:5px; border-radius:8px; border:2px solid transparent; transition:border 0.2s;" onmouseover="this.style.border='2px solid var(--primary-color)'" onmouseout="this.style.border='2px solid transparent'" onclick="insertStickerLocal('${s}')" title="${s}">`
                    ).join('');
                } else {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding:2rem; opacity:0.5; font-size:0.85rem; color:var(--text-muted);">Aún no tienes stickers guardados.</div>';
                }
            } catch(e) { grid.innerHTML = '<div style="grid-column: 1/-1; padding:2rem; color:var(--danger-color);">Error cargando.</div>'; }
        };

        window.toggleStickersMenu = window.cargarStickers; // For backwards compat
        
        window.uploadStickerFromMenu = async function(input) {
            const file = input.files[0];
            if(!file) return;
            const grid = document.getElementById('stickersGrid');
            grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:2rem; opacity:0.5;">⏳ Subiendo...</div>';
            const fd = new FormData();
            fd.append('files', file);
            try {
                const res = await fetch('/api/admin/stickers/upload', { method: 'POST', body: fd });
                if(res.ok) cargarStickers();
            } catch(e) { grid.innerHTML = '<div style="grid-column:1/-1; color:red;">Fallo al subir</div>'; }
        };'''
ibx = ibx.replace(old_toggle_menu, new_toggle_menu)

old_insert_local = '''        window.insertStickerLocal = function(filename) {
            const input = document.getElementById('manualMsgInput');
            if(input) {
                input.value += `[sticker-local:${filename}] `;
                document.getElementById('stickersDrawer').style.display = 'none';
                
                // Auto-enviar la etiqueta (sticker)
                const form = input.closest('form');
                if(form) {
                    const btn = form.querySelector('button[type="submit"]');
                    if(btn) btn.click();
                }
            }
        };'''

new_insert_local = '''        window.insertStickerLocal = function(filename) {
            const input = document.getElementById('manualMsgInput');
            if(input) {
                input.value += `[sticker-local:${filename}] `;
                const m = document.getElementById('emojiMenu');
                if(m) m.style.display = 'none';
                
                // Auto-enviar la etiqueta (sticker)
                const form = input.closest('form');
                if(form) {
                    const btn = form.querySelector('button[type="submit"]');
                    if(btn) btn.click();
                }
            }
        };'''
ibx = ibx.replace(old_insert_local, new_insert_local)

scrollbars = '''
        /* Custom Scrollbar for all */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent; 
        }
        ::-webkit-scrollbar-thumb {
            background: var(--accent-border); 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted); 
        }
'''
if '::-webkit-scrollbar {' not in ibx:
    ibx = ibx.replace('</style>', scrollbars + '\n</style>')

# 2. Width for sidebar-nav from 70px to 55px
ibx = re.sub(r'(\.sidebar-nav\s*\{\s*width:\s*)70px', r'\g<1>55px', ibx)

# 3. Apply pure ESC logic
pure_esc = '''
        // Pure ESC to exit chat
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    window.location.href = `/inbox?tab=${tab}`;
                }
            }
        });
'''
if 'Pure ESC to exit chat' not in ibx:
    idx = ibx.rfind('</script>')
    if idx != -1:
        ibx = ibx[:idx] + pure_esc + '\n' + ibx[idx:]

# 4. User's background-color change
ibx = ibx.replace('--bg-main: #0f172a;', '--bg-main: #213668;')

open('inbox.html', 'w', encoding='utf-8').write(ibx)
print("Complete patch applied")
