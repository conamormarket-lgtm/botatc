import re

code = open('server.py', 'r', encoding='utf-8').read()

# 1. Update emojiMenu
old_emoji_menu = '''                    <!-- Menú Flotante de Emojis -->
                    <div id="emojiMenu" style="display:none; position:absolute; bottom:55px; left:0; z-index:1000; background:transparent; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.15);">
                        <emoji-picker class="light"></emoji-picker>
                    </div>'''

new_emoji_menu = '''                    <!-- Menú Flotante Unificado (Emojis + Stickers) -->
                    <div id="emojiMenu" style="display:none; position:absolute; bottom:55px; left:0; z-index:1000; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.3); flex-direction:column; width:340px; overflow:hidden;">
                        <div style="display:flex; background:var(--accent-bg); border-bottom:1px solid var(--accent-border);">
                            <button type="button" onclick="document.getElementById('emojiTabContent').style.display='block'; document.getElementById('stickerTabContent').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.color='var(--primary-color)'; this.nextElementSibling.style.borderBottom='none'; this.nextElementSibling.style.color='var(--text-muted)';" style="flex:1; padding:0.8rem; background:transparent; border:none; border-bottom:2px solid var(--primary-color); color:var(--primary-color); cursor:pointer; font-weight:600; font-size:0.9rem; transition:color 0.2s;">🙂 Emojis</button>
                            <button type="button" onclick="document.getElementById('stickerTabContent').style.display='block'; document.getElementById('emojiTabContent').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.color='var(--primary-color)'; this.previousElementSibling.style.borderBottom='none'; this.previousElementSibling.style.color='var(--text-muted)'; cargarStickers();" style="flex:1; padding:0.8rem; background:transparent; border:none; border-bottom:none; color:var(--text-muted); cursor:pointer; font-weight:600; font-size:0.9rem; transition:color 0.2s;">⭐ Stickers</button>
                        </div>
                        <div id="emojiTabContent" style="display:block;">
                            <emoji-picker class="light" style="width:100%; border:none; --background:var(--bg-main);"></emoji-picker>
                        </div>
                        <div id="stickerTabContent" class="custom-scrollbar" style="display:none; padding:1rem; width:100%; height:330px; overflow-y:auto; box-sizing:border-box;">
                            <div id="stickersGrid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 0.8rem; justify-items: center;"></div>
                            <div style="margin-top:1rem; text-align:center;">
                                <label style="background:rgba(255,255,255,0.07); border:1px dashed var(--accent-border); color:var(--text-muted); font-size:0.75rem; padding:0.5rem 1rem; border-radius:6px; cursor:pointer; display:inline-block; transition:background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.07)'">
                                    + Subir Nuevo Sticker (.webp/png)
                                    <input type="file" accept="image/webp, image/png" style="display:none;" onchange="uploadStickerFromMenu(this)">
                                </label>
                            </div>
                        </div>
                    </div>'''
code = code.replace(old_emoji_menu, new_emoji_menu)

# 2. Delete Stickers button from attachMenu
old_attach_sticker_btn = '''                        <button type="button" onclick="document.getElementById('attachMenu').style.display='none'; toggleStickersMenu();" style="padding:0.7rem 1rem; border:none; background:transparent; cursor:pointer; text-align:left; color:var(--text-main); font-size:0.9rem; border-radius:8px; transition:background 0.2s; display:flex; align-items:center; gap:0.6rem;" onmouseover="this.style.background='var(--accent-hover-soft)'" onmouseout="this.style.background='transparent'">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg> Stickers
                        </button>'''
code = code.replace(old_attach_sticker_btn, "")

# 3. Remove stickersDrawer
old_drawer = '''                <div id="stickersDrawer" style="display:none; padding:1.5rem; background:var(--bg-main); border-top:1px solid var(--accent-border); height:220px; overflow-y:auto; overflow-x:hidden;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                        <span style="font-weight:600; color:var(--text-main);">Librería de Stickers Locales</span>
                    </div>
                    <div id="stickersGrid" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 1rem; justify-items: center;"></div>
                </div>'''
code = code.replace(old_drawer, "")

open('server.py', 'w', encoding='utf-8').write(code)

ibx = open('inbox.html', 'r', encoding='utf-8').read()

# 4. Inject script logic for sticker
# Just replace toggleStickersMenu definition
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

# 5. Fix insertStickerLocal dismissing old drawer and instead toggle emojiMenu off
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

# 6. Add universal Scrollbar styling inside <style>
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
ibx = ibx.replace('</style>', scrollbars + '\n</style>')

open('inbox.html', 'w', encoding='utf-8').write(ibx)

print("Patch inbox logic successful")
