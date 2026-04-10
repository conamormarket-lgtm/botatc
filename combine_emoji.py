import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""                <!-- IZQUIERDA: Emojis y Stickers -->
                <div style="flex:0 0 auto; display:flex; gap:0.1rem;">
                    <!-- Emoji Button -->
                    <button type="button" onclick="const m = document.getElementById('emojiMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Emojis">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                    </button>
                    <!-- Sticker Button -->
                    <button type="button" onclick="const m = document.getElementById('stickerMenu'); m.style.display = m.style.display==='none'?'flex':'none';" style="background:transparent; border:none; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Stickers">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5"></path><path d="M8.5 8.5v.01"></path><path d="M16 15.5v.01"></path><path d="M12 12v.01"></path><path d="M11 17a4.5 4.5 0 0 0 5-3"></path></svg>
                    </button>
                </div>"""

rep = r"""                <!-- IZQUIERDA: Combinado Emoji/Sticker -->
                <div style="flex:0 0 auto; display:flex; position:relative;">
                    <button type="button" onclick="const m = document.getElementById('combinedEmojiMenu'); m.style.display = m.style.display==='none'?'flex':'none'; if(m.style.display==='flex') { document.getElementById('btnTabEmoji').click(); if(window.cargarStickers) window.cargarStickers(); }" style="background:transparent; border:none; width:46px; height:46px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-muted); transition:color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'" title="Emojis y Stickers">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
                    </button>

                    <!-- Popover combinado -->
                    <div id="combinedEmojiMenu" style="display:none; position:absolute; bottom:calc(100% + 0.5rem); left:0; width:320px; height:380px; background:var(--bg-main); border:1px solid var(--accent-border); border-radius:16px; box-shadow:0 8px 16px rgba(0,0,0,0.5); z-index:100; flex-direction:column; overflow:hidden;">
                        <!-- Tab Headers -->
                        <div style="display:flex; border-bottom:1px solid var(--accent-border); background:var(--accent-bg);">
                            <button type="button" id="btnTabEmoji" onclick="document.getElementById('tabEmoji').style.display='flex'; document.getElementById('tabSticker').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.opacity='1'; document.getElementById('btnTabSticker').style.borderBottom='2px solid transparent'; document.getElementById('btnTabSticker').style.opacity='0.6';" style="flex:1; padding:0.8rem; background:transparent; border:none; cursor:pointer; color:var(--text-main); font-weight:600; border-bottom:2px solid var(--primary-color); outline:none;">Emojis</button>
                            <button type="button" id="btnTabSticker" onclick="document.getElementById('tabSticker').style.display='flex'; document.getElementById('tabEmoji').style.display='none'; this.style.borderBottom='2px solid var(--primary-color)'; this.style.opacity='1'; document.getElementById('btnTabEmoji').style.borderBottom='2px solid transparent'; document.getElementById('btnTabEmoji').style.opacity='0.6';" style="flex:1; padding:0.8rem; background:transparent; border:none; cursor:pointer; color:var(--text-main); font-weight:600; border-bottom:2px solid transparent; opacity:0.6; outline:none;">Stickers</button>
                        </div>
                        <!-- Tab Contents -->
                        <div style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                            <!-- Emoji Tab -->
                            <div id="tabEmoji" style="flex:1; display:flex; flex-direction:column; overflow:hidden;">
                                <emoji-picker style="width:100%; height:100%; --background: var(--bg-main); --border-color: transparent;"></emoji-picker>
                            </div>
                            <!-- Sticker Tab -->
                            <div id="tabSticker" style="flex:1; display:none; flex-direction:column; overflow-y:auto; padding:0.5rem; background:var(--bg-sidebar);">
                                <div id="stickersGrid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(70px, 1fr)); gap:5px; padding-bottom:1rem;">
                                    <div style="grid-column:1/-1; text-align:center; padding:1rem; opacity:0.5; color:var(--text-muted); font-size:0.85rem;">Cargando...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""

if target in text:
    text = text.replace(target, rep)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Combined menu applied!")
else:
    print("Target not found.")

