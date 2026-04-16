with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find start and end lines (1-indexed in view = 0-indexed in list)
start = 3857 - 1  # "var c = document.getElementById('chatScroll');"
end   = 3905 - 1  # closing "}}" line

# Verify
print("START line:", repr(lines[start].rstrip()))
print("END   line:", repr(lines[end].rstrip()))

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
                        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        el.style.transition = 'all 0.5s ease';
                        el.style.boxShadow = '0 0 0 4px var(--primary-color)';
                        el.style.transform = 'scale(1.02)';
                        setTimeout(() => el.scrollIntoView({{ behavior: 'smooth', block: 'center' }}), 600);
                        setTimeout(() => el.scrollIntoView({{ behavior: 'smooth', block: 'center' }}), 1200);
                        setTimeout(() => {{
                            el.style.boxShadow = '';
                            el.style.transform = 'scale(1)';
                            setTimeout(() => window._isSearching = false, 1500);
                        }}, 2800);
                    }}

                    // Polling: hasta 40 intentos cada 150ms (= 6s maximo)
                    // Necesario porque con historico completo el DOM puede tardar en renderizarse
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

print("OK - Reemplazo exitoso")
