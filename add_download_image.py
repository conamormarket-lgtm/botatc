import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add HTML Item
html_old = '''<div class="ctx-item" id="ctxCopyImage"
            style="display:none; padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); align-items:center; gap:0.5rem; transition:background 0.2s; border-bottom:1px solid var(--accent-border);">'''

html_new = '''<div class="ctx-item" id="ctxDownloadImage"
            style="display:none; padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); align-items:center; gap:0.5rem; transition:background 0.2s; border-bottom:1px solid var(--accent-border);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Descargar Imagen
        </div>

        <div class="ctx-item" id="ctxCopyImage"
            style="display:none; padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; color:var(--text-main); align-items:center; gap:0.5rem; transition:background 0.2s; border-bottom:1px solid var(--accent-border);">'''

if 'id="ctxDownloadImage"' not in text:
    text = text.replace(html_old, html_new)

# 2. Update display logic
logic_old = '''let ctxCopyImage = document.getElementById("ctxCopyImage");
                if (regularImg && !stickerImg) {
                    ctxTargetImageUrl = regularImg.src;
                    ctxCopyImage.style.display = 'flex';
                } else {
                    ctxTargetImageUrl = "";
                    ctxCopyImage.style.display = 'none';
                }'''

logic_new = '''let ctxCopyImage = document.getElementById("ctxCopyImage");
                let ctxDownloadImage = document.getElementById("ctxDownloadImage");
                if (regularImg && !stickerImg) {
                    ctxTargetImageUrl = regularImg.src;
                    ctxCopyImage.style.display = 'flex';
                    ctxDownloadImage.style.display = 'flex';
                } else {
                    ctxTargetImageUrl = "";
                    ctxCopyImage.style.display = 'none';
                    ctxDownloadImage.style.display = 'none';
                }'''

text = text.replace(logic_old, logic_new)

# 3. Inject event listener
click_old = '''} catch(e) {
                console.error("Error copy image", e);
                alert("No se pudo copiar la imagen.");
            }
        });'''

click_new = '''} catch(e) {
                console.error("Error copy image", e);
                alert("No se pudo copiar la imagen.");
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
                alert("Ocurrió un error al descargar la imagen.");
            }
        });'''

if 'ctxDownloadImage").addEventListener' not in text:
    text = text.replace(click_old, click_new)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Descargar Imagen logic injected.")
