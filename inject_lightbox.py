import re

with open("inbox.html", "r", encoding="utf-8") as f:
    html = f.read()

lightbox_html = """
    <!-- Lightbox para imágenes -->
    <div id="imageLightbox" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; align-items:center; justify-content:center; flex-direction:column; cursor:pointer;" onclick="if(event.target === this) this.style.display='none'">
        <button onclick="document.getElementById('imageLightbox').style.display='none'" style="position:absolute; top:20px; right:30px; background:none; border:none; color:white; font-size:2.5rem; cursor:pointer; text-shadow:0 2px 4px rgba(0,0,0,0.5);">&times;</button>
        <img id="lightboxImg" src="" style="max-width:90%; max-height:90%; border-radius:8px; box-shadow:0 10px 40px rgba(0,0,0,0.7); cursor:default;" oncontextmenu="event.stopPropagation();">
    </div>

    <!-- Script de Lightbox -->
    <script>
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
    </script>
</body>"""

if "id=\"imageLightbox\"" not in html:
    new_html = html.replace("</body>", lightbox_html)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Lightbox injected!")
else:
    print("Already there")
