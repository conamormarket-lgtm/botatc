with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = 3775 - 1
end   = 3840 - 1

print("START:", repr(lines[start].rstrip()))
print("END  :", repr(lines[end].rstrip()))

new_block = """\
            var c = document.getElementById('chatScroll');
            if(c) {{
                const params = new URLSearchParams(window.location.search);
                const msgId = params.get('msg_id');
                if (msgId) {{
                    // Marcar que este chat tiene historico completo cargado.
                    // El polling lo usara para seguir pidiendo history=all indefinidamente,
                    // evitando que el chat vuelva a los 70 mensajes recientes.
                    window._viewingAllHistory = true;

                    // Limpiar param de URL (sin recargar)
                    const url = new URL(window.location);
                    url.searchParams.delete('msg_id');
                    window.history.replaceState({{}}, '', url);

                    // Scroll con retry hasta encontrar el elemento
                    let attempts = 0;
                    function tryScroll() {{
                        const el = document.getElementById('msg-' + msgId);
                        if (el) {{
                            requestAnimationFrame(() => requestAnimationFrame(() => {{
                                el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                                el.style.transition = 'all 0.5s ease';
                                el.style.boxShadow = '0 0 0 4px var(--primary-color)';
                                el.style.transform = 'scale(1.02)';
                                setTimeout(() => {{
                                    el.style.boxShadow = '';
                                    el.style.transform = 'scale(1)';
                                }}, 2800);
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

print("OK")
