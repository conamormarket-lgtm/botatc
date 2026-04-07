import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Clean up ALL spaces inside template curly braces that broke via formatter
# Like { \n chat_view_css \n } -> {chat_view_css}
broken_vars = [
    'color_global', 'tab_all_active', 'tab_human_active', 
    'labels_filter_html', 'chat_view_css', 'body_class', 
    'lista_chats_html', 'chat_viewer_html'
]

for var in broken_vars:
    # re to match `{ [spaces/newlines] var [spaces/newlines] }`
    html = re.sub(r'\{\s*' + var + r'\s*\}', '{' + var + '}', html)

# Fix `;` floating around after {color_global} if it was added like `} ;`
html = re.sub(r'\{\s*color_global\s*\}\s*;', '{color_global};', html)

# 2. Fix skeletons 
# Removing any skeleton CSS and logic
html = re.sub(r'\s*\.skeleton \{.*?\n\s*\}\s*@keyframes skeleton-loading \{.*?\n\s*\}\s*', '', html, flags=re.DOTALL)
html = re.sub(r'\s*// --- NAVEGACIÓN Y SKELETONS ---.*?\}\);\s*', '', html, flags=re.DOTALL)

# Let's ensure pure ESC logic exists
pure_esc = '''
        // Pure ESC to exit chat
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                if (window.location.pathname !== '/inbox' && window.location.pathname.startsWith('/inbox/')) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const tab = urlParams.get('tab') || 'all';
                    window.location.href = `/inbox?tab=${tab}`;
                }
            }
        });
'''
if 'Pure ESC to exit chat' not in html:
    idx = html.rfind('</script>')
    if idx != -1:
        html = html[:idx] + pure_esc + '\n' + html[idx:]

# 3. Apply the glorious color palette
# Replace :root { ... } with our refined blue palette
new_root = '''        :root {
            /* 1. Nivel de Color Principal */
            --primary-color: #3b82f6;       
            --primary-hover: #2563eb;       
            /* 2. Nivel de Color de Acento (translúcidos adaptables) */
            --accent-bg: rgba(255, 255, 255, 0.05);           
            --accent-border: rgba(255, 255, 255, 0.1);       
            --accent-hover-soft: rgba(255, 255, 255, 0.08);   
            /* 3. Nivel de Color de Fondo General */
            --bg-main: #213668;             
            --bg-sidebar: #17264a;
            --bg-list: #1b2d56;
            /* 4. Tipografías */
            --font-main: 'Inter', sans-serif;
            --font-heading: 'Outfit', sans-serif;
            /* 5. Texto y Estados */
            --text-main: #f8fafc;           
            --text-muted: #cbd5e1;          
            --danger-color: #ef4444;        
            --success-color: #10b981;       
        }'''
html = re.sub(r':root\s*\{.*?(?=\s*/\*\s*RESET Y BASE)', new_root, html, flags=re.DOTALL)

# 4. Apply background colors to specific panels to give depth
html = re.sub(r'(\.sidebar-nav\s*\{[^\}]*)', r'\1\n            background-color: var(--bg-sidebar);', html)
html = re.sub(r'(\.chat-list-panel\s*\{[^\}]*)', r'\1\n            background-color: var(--bg-list);', html)

# Clean up duplications if any ran before
html = re.sub(r'background-color: var\(--bg-sidebar\);\s*background-color: var\(--bg-sidebar\);', 'background-color: var(--bg-sidebar);', html)
html = re.sub(r'background-color: var\(--bg-list\);\s*background-color: var\(--bg-list\);', 'background-color: var(--bg-list);', html)


with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Beautified and Fixed!")
