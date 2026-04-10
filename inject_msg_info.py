import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    html = f.read()

# ─── 1. CSS PARA EL PANEL info ───────────────────────────────────────
css = """
        /* ─── Panel de Info de Mensaje ─── */
        #msg-info-panel {
            position: fixed; top: 0; right: -360px; width: 340px; height: 100%;
            background: var(--bg-card, #1e293b); border-left: 1px solid var(--accent-border, rgba(255,255,255,0.1));
            z-index: 1000; transition: right 0.3s ease; display: flex; flex-direction: column;
            box-shadow: -4px 0 20px rgba(0,0,0,0.4);
        }
        #msg-info-panel.open { right: 0; }
        #msg-info-panel .info-header {
            padding: 20px; border-bottom: 1px solid var(--accent-border, rgba(255,255,255,0.1));
            display: flex; justify-content: space-between; align-items: center;
        }
        #msg-info-panel .info-header h3 {
            margin: 0; font-family: 'Outfit', sans-serif; font-size: 1.1rem; color: var(--text-main, #f8fafc);
        }
        #msg-info-panel .info-close-btn {
            background: none; border: none; font-size: 1.4rem; color: var(--text-muted, #94a3b8);
            cursor: pointer; line-height: 1; transition: color 0.2s;
        }
        #msg-info-panel .info-close-btn:hover { color: var(--text-main, #f8fafc); }
        #msg-info-panel .info-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; flex: 1; }
        .info-row { display: flex; flex-direction: column; gap: 4px; }
        .info-row .info-label {
            font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
            color: var(--text-muted, #94a3b8); font-weight: 600;
        }
        .info-row .info-value {
            font-size: 0.95rem; color: var(--text-main, #f8fafc);
            display: flex; align-items: center; gap: 8px;
        }
        .info-row .info-value .icon { font-size: 1.1rem; }
        .info-preview {
            background: var(--bg-main, #0f172a); border-radius: 10px; padding: 12px 16px;
            font-size: 0.85rem; color: var(--text-muted, #94a3b8); max-height: 120px;
            overflow: hidden; line-height: 1.5; word-break: break-word;
            border-left: 3px solid var(--primary-color, #3b82f6);
        }
        /* Mini menú contextual */
        #msg-ctx-menu {
            position: fixed; background: #1e293b; border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); z-index: 9999;
            overflow: hidden; display: none; min-width: 160px;
        }
        .ctx-menu-item {
            padding: 11px 18px; cursor: pointer; font-size: 0.88rem; color: #f8fafc;
            display: flex; align-items: center; gap: 10px; transition: background 0.15s;
        }
        .ctx-menu-item:hover { background: rgba(255,255,255,0.08); }
"""

# Insert before closing </style> of head
html = html.replace('</style>', css + '\n        </style>', 1)

# ─── 2. HTML: PANEL + MINI MENÚ ───────────────────────────────────────
panel_html = """
    <!-- Panel de info de mensaje -->
    <div id="msg-info-panel">
        <div class="info-header">
            <h3>ℹ️ Info del Mensaje</h3>
            <button class="info-close-btn" onclick="closeMsgInfoPanel()">✕</button>
        </div>
        <div class="info-body">
            <div class="info-preview" id="info-preview-text">—</div>
            <div class="info-row">
                <span class="info-label">Enviado por</span>
                <span class="info-value"><span class="icon">👤</span><span id="info-sent-by">—</span></span>
            </div>
            <div class="info-row">
                <span class="info-label">Hora de envío</span>
                <span class="info-value"><span class="icon">📤</span><span id="info-sent-ts">—</span></span>
            </div>
            <div class="info-row">
                <span class="info-label">Entregado</span>
                <span class="info-value"><span class="icon">✓✓</span><span id="info-delivered-ts">—</span></span>
            </div>
            <div class="info-row">
                <span class="info-label">Leído</span>
                <span class="info-value"><span class="icon" style="color:#34b7f1">✓✓</span><span id="info-read-ts">—</span></span>
            </div>
        </div>
    </div>

    <!-- Mini menú contextual -->
    <div id="msg-ctx-menu">
        <div class="ctx-menu-item" id="ctx-info-btn">
            <span>ℹ️</span> Información
        </div>
    </div>
"""
html = html.replace('</body>', panel_html + '\n</body>')

# ─── 3. JS ────────────────────────────────────────────────────────────
js = """
        // ─── Info panel de mensajes ────────────────────────────────────────
        let _ctxTarget = null;

        function formatTsUnix(ts) {
            if (!ts) return '—';
            const d = new Date(ts * 1000);
            return d.toLocaleString('es-PE', {hour:'2-digit', minute:'2-digit', day:'2-digit', month:'short', year:'numeric'});
        }

        function openMsgInfoPanel(bubble) {
            const sentBy = bubble.dataset.sentBy || '—';
            const ts = bubble.dataset.ts;
            const deliveredTs = bubble.dataset.deliveredTs;
            const readTs = bubble.dataset.readTs;
            const preview = bubble.innerText.replace(bubble.querySelector('.msg-meta')?.innerText || '', '').trim().slice(0, 200);

            document.getElementById('info-preview-text').textContent = preview || '—';
            document.getElementById('info-sent-by').textContent = sentBy || '—';
            document.getElementById('info-sent-ts').textContent = formatTsUnix(ts);
            document.getElementById('info-delivered-ts').textContent = formatTsUnix(deliveredTs);
            document.getElementById('info-read-ts').textContent = formatTsUnix(readTs);

            document.getElementById('msg-info-panel').classList.add('open');
        }

        function closeMsgInfoPanel() {
            document.getElementById('msg-info-panel').classList.remove('open');
        }

        // Hook: click derecho en burbujas bot
        document.addEventListener('contextmenu', function(e) {
            const bubble = e.target.closest('.bubble-bot');
            if (bubble && bubble.dataset.sentBy !== undefined) {
                e.preventDefault();
                _ctxTarget = bubble;
                const menu = document.getElementById('msg-ctx-menu');
                menu.style.display = 'block';
                let x = e.clientX, y = e.clientY;
                if (x + 180 > window.innerWidth) x = window.innerWidth - 190;
                if (y + 60 > window.innerHeight) y = window.innerHeight - 70;
                menu.style.left = x + 'px';
                menu.style.top = y + 'px';
                return false;
            }
        });

        document.getElementById('ctx-info-btn').addEventListener('click', function() {
            document.getElementById('msg-ctx-menu').style.display = 'none';
            if (_ctxTarget) openMsgInfoPanel(_ctxTarget);
        });

        document.addEventListener('click', function(e) {
            const menu = document.getElementById('msg-ctx-menu');
            if (!menu.contains(e.target)) menu.style.display = 'none';
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.getElementById('msg-ctx-menu').style.display = 'none';
                closeMsgInfoPanel();
            }
        });
"""

# Insert before last </script>
last_script = html.rfind('</script>')
if last_script != -1:
    html = html[:last_script] + js + '\n        </script>' + html[last_script+9:]

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Inyectado panel de info de mensaje")
