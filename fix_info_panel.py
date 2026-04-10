import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Remove the duplicate mini menu I added before
html = re.sub(r'\s*<!-- Mini menú contextual -->\s*<div id="msg-ctx-menu">.*?</div>', '', html, flags=re.DOTALL)

# 2. Remove old duplicate css for #msg-ctx-menu and .ctx-menu-item since the existing ones are .ctx-item
html = re.sub(r'/\* Mini menú contextual \*/.*?\.ctx-menu-item:hover \{.*?\}', '', html, flags=re.DOTALL)

# 3. Remove old JS block I added (the one with openMsgInfoPanel, ctx-info-btn etc.)
html = re.sub(r'// ─── Info panel de mensajes ────.*?document\.addEventListener\(\'keydown\'.*?\}\);', '', html, flags=re.DOTALL)

# 4. Find the last ctx-item before closing </div> of bubbleContextMenu and add ours
# We need to find "Copiar Texto" item (last item) and add "Información" after it
insert_after = 'id="ctxCopyText"'
idx = html.find(insert_after)
if idx != -1:
    # find end of this ctx-item closing tag
    close_div = html.find('</div>', idx)
    info_item = """
        <div class="ctx-item" id="ctxMsgInfo"
            style="padding:0.8rem 1rem; cursor:pointer; font-size:0.95rem; border-top:1px solid var(--accent-border); color:var(--text-main); display:none; align-items:center; gap:0.5rem; transition:background 0.2s;"
            onmouseover="this.style.background='var(--accent-bg)'" onmouseout="this.style.background=''">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <strong>Información</strong>
        </div>"""
    html = html[:close_div+6] + info_item + html[close_div+6:]
    print(f"Inserted info item after ctxCopyText")
else:
    print("Could not find ctxCopyText to insert after")

# 5. In the contextmenu handler, after `ctxTargetWamid = bubble.getAttribute('data-wamid');` 
# add code to capture bubble ref and show/hide ctxMsgInfo
old_capture = "ctxTargetWamid = bubble.getAttribute('data-wamid');"
new_capture = """ctxTargetWamid = bubble.getAttribute('data-wamid');
                ctxTargetBubble = bubble;
                
                // Show Información only for bot messages with data-sent-by
                const infoItem = document.getElementById('ctxMsgInfo');
                if (infoItem) {
                    infoItem.style.display = bubble.classList.contains('bubble-bot') && bubble.dataset.sentBy !== undefined ? 'flex' : 'none';
                }"""
html = html.replace(old_capture, new_capture)

# 6. Find where ctxTargetWamid is declared and add ctxTargetBubble
html = html.replace("let ctxTargetMediaId = \"\";", "let ctxTargetMediaId = \"\";\n        let ctxTargetBubble = null;")

# 7. Update the JS for the info panel to connect to ctxMsgInfo click
info_js = """
        // ─── Panel de Info de Mensaje ───────────────────────────────
        function formatTsUnix(ts) {
            if (!ts) return '—';
            const d = new Date(parseInt(ts) * 1000);
            return d.toLocaleString('es-PE', {
                hour: '2-digit', minute: '2-digit',
                day: '2-digit', month: 'short', year: 'numeric'
            });
        }

        function openMsgInfoPanel(bubble) {
            const sentBy = bubble.dataset.sentBy || '—';
            const ts = bubble.dataset.ts || '';
            const deliveredTs = bubble.dataset.deliveredTs || '';
            const readTs = bubble.dataset.readTs || '';
            // Get text without meta (timestamp/ticks)
            const clone = bubble.cloneNode(true);
            const metaEl = clone.querySelector('.msg-meta');
            if (metaEl) metaEl.remove();
            const preview = clone.innerText.trim().slice(0, 200);

            document.getElementById('info-preview-text').textContent = preview || '—';
            document.getElementById('info-sent-by').textContent = sentBy;
            document.getElementById('info-sent-ts').textContent = formatTsUnix(ts);
            document.getElementById('info-delivered-ts').textContent = deliveredTs ? formatTsUnix(deliveredTs) : '—';
            document.getElementById('info-read-ts').textContent = readTs ? formatTsUnix(readTs) : '—';

            document.getElementById('msg-info-panel').classList.add('open');
        }

        function closeMsgInfoPanel() {
            document.getElementById('msg-info-panel').classList.remove('open');
        }

        const ctxInfoBtn = document.getElementById('ctxMsgInfo');
        if (ctxInfoBtn) {
            ctxInfoBtn.addEventListener('click', function() {
                document.getElementById('bubbleContextMenu').style.display = 'none';
                if (ctxTargetBubble) openMsgInfoPanel(ctxTargetBubble);
            });
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeMsgInfoPanel();
        });
"""

# Insert before last </script>
last_script = html.rfind('</script>')
if last_script != -1:
    html = html[:last_script] + info_js + '\n        </script>' + html[last_script+9:]
    print("Inserted info panel JS")

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done")
