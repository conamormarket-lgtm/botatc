# Reemplaza el bloque de scroll JS en server.py usando numeros de linea exactos
with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verificar los limites correctos
start = 3775 - 1  # "var c = document.getElementById('chatScroll');"
end   = 3823 - 1  # closing "}}" (inclusive)

print("START:", repr(lines[start].rstrip()))
print("END  :", repr(lines[end].rstrip()))

new_block = """\
            var c = document.getElementById('chatScroll');
            if(c) {{
                const params = new URLSearchParams(window.location.search);
                const msgId = params.get('msg_id');
                if (msgId) {{
                    // Limpiar param de URL de inmediato
                    const url = new URL(window.location);
                    url.searchParams.delete('msg_id');
                    window.history.replaceState({{}}, '', url);

                    function highlightAndScroll(el) {{
                        window._isSearching = true;
                        // Scroll instantaneo para la posicion inicial (no smooth, para no competir luego)
                        el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                        el.style.transition = 'all 0.5s ease';
                        el.style.boxShadow = '0 0 0 4px var(--primary-color)';
                        el.style.transform = 'scale(1.02)';

                        // Re-anclar cuando las imagenes terminen de cargar (causan layout shift)
                        const imgs = c.querySelectorAll('img');
                        imgs.forEach(img => {{
                            if (!img.complete) {{
                                img.addEventListener('load', () => {{
                                    if (window._isSearching) el.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                                }}, {{ once: true }});
                            }}
                        }});

                        // ResizeObserver: re-anclar ante cualquier cambio de altura del chat
                        let resizeTimer;
                        const ro = new ResizeObserver(() => {{
                            if (!window._isSearching) {{ ro.disconnect(); return; }}
                            clearTimeout(resizeTimer);
                            resizeTimer = setTimeout(() => el.scrollIntoView({{ behavior: 'instant', block: 'center' }}), 80);
                        }});
                        ro.observe(c);

                        // Apagar highlight y ResizeObserver tras 5 segundos
                        setTimeout(() => {{
                            el.style.boxShadow = '';
                            el.style.transform = 'scale(1)';
                            setTimeout(() => {{
                                window._isSearching = false;
                                ro.disconnect();
                            }}, 1500);
                        }}, 3500);
                    }}

                    // Polling: hasta 40 intentos cada 150ms (= 6s maximo)
                    let attempts = 0;
                    function tryScroll() {{
                        const el = document.getElementById('msg-' + msgId);
                        if (el) {{
                            requestAnimationFrame(() => requestAnimationFrame(() => highlightAndScroll(el)));
                        }} else if (attempts < 40) {{
                            attempts++;
                            setTimeout(tryScroll, 150);
                        }} else {{
                            c.scrollTop = c.scrollHeight;
                        }}
                    }}
                    tryScroll();
                }} else {{
                    c.scrollTop = c.scrollHeight;
                }}
            }}
"""

lines[start:end+1] = [new_block]

with open('server.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("OK - Reemplazo aplicado")
