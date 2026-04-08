import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add variable ctxTargetImageUrl
if 'let ctxTargetImageUrl = "";' not in text:
    text = text.replace('let ctxTargetMediaId = "";', 'let ctxTargetMediaId = "";\n        let ctxTargetImageUrl = "";')

# 2. Add context menu item logic
copy_txt_logic = '''document.getElementById("ctxCopy").addEventListener("click", function () {
            document.getElementById("bubbleContextMenu").style.display = "none";
            navigator.clipboard.writeText(ctxTargetText.trim());
        });'''

copy_img_logic = '''document.getElementById("ctxCopy").addEventListener("click", function () {
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
                        alert("El navegador bloqueó la copia de la imagen.");
                    }
                }, 'image/png');
            } catch(e) {
                console.error("Error copy image", e);
                alert("No se pudo copiar la imagen.");
            }
        });'''

if 'ctxCopyImage' not in text:
    text = text.replace(copy_txt_logic, copy_img_logic)

# 3. Add context menu HTML element
element_old = '''<div class="ctx-item" id="ctxCopy"
            style="padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); display:flex; align-items:center; gap:0.5rem; transition:background 0.2s;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
            </svg>
            Copiar Texto
        </div>'''

element_new = '''<div class="ctx-item" id="ctxCopyImage"
            style="display:none; padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); align-items:center; gap:0.5rem; transition:background 0.2s; border-bottom:1px solid var(--accent-border);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
            </svg>
            Copiar Imagen
        </div>

        <div class="ctx-item" id="ctxCopy"
            style="padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); display:flex; align-items:center; gap:0.5rem; transition:background 0.2s;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
            </svg>
            Copiar Texto
        </div>'''

if 'id="ctxCopyImage"' not in text:
    text = text.replace(element_old, element_new)

# 4. Show/hide logic inside contextmenu event
display_logic_old = '''} else {
                    ctxTargetMediaId = "";
                    ctxSaveSticker.style.display = 'none';
                }

                const cm = document.getElementById("bubbleContextMenu");'''

display_logic_new = '''} else {
                    ctxTargetMediaId = "";
                    ctxSaveSticker.style.display = 'none';
                }

                let regularImg = bubble.querySelector('img[alt^="Imagen"]');
                let ctxCopyImage = document.getElementById("ctxCopyImage");
                if (regularImg && !stickerImg) {
                    ctxTargetImageUrl = regularImg.src;
                    ctxCopyImage.style.display = 'flex';
                } else {
                    ctxTargetImageUrl = "";
                    ctxCopyImage.style.display = 'none';
                }

                const cm = document.getElementById("bubbleContextMenu");'''

if 'ctxTargetImageUrl = regularImg.src;' not in text:
    text = text.replace(display_logic_old, display_logic_new)

with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added Copiar Imagen feature")
