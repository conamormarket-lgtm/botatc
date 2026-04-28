with open('server.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_fn = (
    'async function cargarQuickReplies(forceRefresh) {{\n'
    '                const list = document.getElementById("quickRepliesList");\n'
    '                if(!list) return;\n'
    '                const activeLine = window.ACTIVE_CHAT_LINE || "principal";\n'
    '                // Usar cache si ya hay datos de la misma linea y no se fuerza refresco\n'
    '                if(!forceRefresh && quickRepliesCache && quickRepliesCache.length > 0\n'
    '                   && window._qrCacheLine === activeLine) {{\n'
    '                    renderQuickReplies(quickRepliesCache);\n'
    '                    return;\n'
    '                }}\n'
    '                list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando respuestas...</div>`;\n'
    '                try {{\n'
    '                    // Cargar labels solo si no tenemos o cambio la linea\n'
    '                    const needsLabels = !window._globalLabels || window._qrCacheLine !== activeLine;\n'
    '                    const fetches = [fetch("/api/quick-replies?line=" + activeLine)];\n'
    '                    if(needsLabels) fetches.push(fetch("/api/admin/labels/list"));\n'
    '                    const results = await Promise.all(fetches);\n'
    '                    const resQr = results[0];\n'
    '                    if (!resQr.ok) throw new Error("HTTP " + resQr.status);\n'
    '                    const data = await resQr.json();\n'
    '                    if(needsLabels && results[1] && results[1].ok) {{\n'
    '                        const lblData = await results[1].json();\n'
    '                        window._globalLabels = Array.isArray(lblData) ? lblData : (lblData.labels || []);\n'
    '                    }}\n'
    '                    quickRepliesCache = data;\n'
    '                    window._qrCacheLine = activeLine;\n'
    '                    renderQuickReplies(data);\n'
    '                }} catch(e) {{\n'
    '                    list.innerHTML = `<div style="font-size:0.85rem; color:red; padding:1rem; text-align:center; background:rgba(255,0,0,0.1); border-radius:8px;">Error: ${{e.message}}</div>`;\n'
    '                }}\n'
    '            }}'
)

new_fn = (
    'async function cargarQuickReplies(forceRefresh) {{\n'
    '                const list = document.getElementById("quickRepliesList");\n'
    '                if(!list) return;\n'
    '                const activeLine = window.ACTIVE_CHAT_LINE || "principal";\n'
    '                const SS_KEY = "qrCache_" + activeLine;\n'
    '                const SS_LBL = "qrLabels";\n'
    '                const SS_TS  = "qrCacheTs_" + activeLine;\n'
    '                const MAX_AGE_MS = 5 * 60 * 1000; // 5 minutos\n'
    '                // ── Intentar usar sessionStorage primero ──────────────────\n'
    '                if(!forceRefresh) {{\n'
    '                    const cached = sessionStorage.getItem(SS_KEY);\n'
    '                    const ts     = parseInt(sessionStorage.getItem(SS_TS) || "0");\n'
    '                    if(cached && (Date.now() - ts) < MAX_AGE_MS) {{\n'
    '                        try {{\n'
    '                            const data = JSON.parse(cached);\n'
    '                            const lblRaw = sessionStorage.getItem(SS_LBL);\n'
    '                            if(lblRaw) window._globalLabels = JSON.parse(lblRaw);\n'
    '                            quickRepliesCache = data;\n'
    '                            renderQuickReplies(data);\n'
    '                            return; // Instantaneo - sin API call\n'
    '                        }} catch(e) {{ /* cache corrupto, refrescar */ }}\n'
    '                    }}\n'
    '                }}\n'
    '                // ── Sin cache valido: fetch a la API ─────────────────────\n'
    '                list.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center;">Cargando respuestas...</div>`;\n'
    '                try {{\n'
    '                    const [resQr, resLbl] = await Promise.all([\n'
    '                        fetch("/api/quick-replies?line=" + activeLine),\n'
    '                        fetch("/api/admin/labels/list")\n'
    '                    ]);\n'
    '                    if (!resQr.ok) throw new Error("HTTP " + resQr.status);\n'
    '                    const data = await resQr.json();\n'
    '                    const lblData = resLbl.ok ? await resLbl.json() : [];\n'
    '                    window._globalLabels = Array.isArray(lblData) ? lblData : (lblData.labels || []);\n'
    '                    quickRepliesCache = data;\n'
    '                    // Guardar en sessionStorage para proximos cambios de chat\n'
    '                    try {{\n'
    '                        sessionStorage.setItem(SS_KEY, JSON.stringify(data));\n'
    '                        sessionStorage.setItem(SS_LBL, JSON.stringify(window._globalLabels));\n'
    '                        sessionStorage.setItem(SS_TS, Date.now().toString());\n'
    '                    }} catch(e) {{ /* sessionStorage lleno, ignorar */ }}\n'
    '                    renderQuickReplies(data);\n'
    '                }} catch(e) {{\n'
    '                    list.innerHTML = `<div style="font-size:0.85rem; color:red; padding:1rem; text-align:center; background:rgba(255,0,0,0.1); border-radius:8px;">Error: ${{e.message}}</div>`;\n'
    '                }}\n'
    '            }}'
)

if old_fn in c:
    c = c.replace(old_fn, new_fn, 1)
    print('OK: cargarQuickReplies con sessionStorage cache')
else:
    print('NO MATCH')
    idx = c.find('async function cargarQuickReplies')
    print(repr(c[idx:idx+100]))

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(c)

import subprocess
r = subprocess.run(['python', '-m', 'py_compile', 'server.py'], capture_output=True, text=True)
print('Compilacion:', 'OK' if r.returncode == 0 else r.stderr[:300])
