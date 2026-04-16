with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = 3775 - 1
end   = 3820 - 1

print("START:", repr(lines[start].rstrip()))
print("END  :", repr(lines[end].rstrip()))

new_block = """\
            var c = document.getElementById('chatScroll');
            if(c) {{
                const params = new URLSearchParams(window.location.search);
                const msgId = params.get('msg_id');
                if (msgId) {{
                    // Historial completo cargado: el polling seguira pidiendo history=all
                    window._viewingAllHistory = true;

                    // Limpiar param de URL sin recargar
                    const url = new URL(window.location);
                    url.searchParams.delete('msg_id');
                    window.history.replaceState({{}}, '', url);

                    let attempts = 0;
                    function tryScroll() {{
                        const el = document.getElementById('msg-' + msgId);
                        if (el) {{
                            requestAnimationFrame(() => requestAnimationFrame(() => {{
                                // Scroll inicial (instant para evitar que smooth quede a medias)
                                el.scrollIntoView({{ behavior: 'instant', block: 'center' }});

                                // Highlight visual
                                el.style.transition = 'all 0.5s ease';
                                el.style.boxShadow = '0 0 0 4px var(--primary-color)';
                                el.style.transform = 'scale(1.02)';

                                // Re-scroll progresivo: las imagenes cargan y desplazan el layout
                                // Corregir en 4 momentos hasta que el layout se estabilice
                                [400, 900, 1600, 2600].forEach(delay => {{
                                    setTimeout(() => {{
                                        const target = document.getElementById('msg-' + msgId);
                                        if (target) target.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                                    }}, delay);
                                }});

                                // Quitar highlight despues de 3.5s
                                setTimeout(() => {{
                                    el.style.boxShadow = '';
                                    el.style.transform = 'scale(1)';
                                }}, 3500);
                            }}));
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

print("OK - aplicado")
