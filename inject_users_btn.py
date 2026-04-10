import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

html = open("inbox.html", "r", encoding="utf-8").read()

# For admin users, add /usuarios button just after /settings
usuarios_btn = """
        <!-- Admin Users Icon -->
        <a href="/usuarios" class="nav-item" title="Panel de Usuarios">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
        </a>
"""

if "<!-- Admin Users Icon -->" not in html:
    html = html.replace('title="Personalizar Agente IA">', 'title="Personalizar Agente IA">') # Dummy
    # Let's insert it before <div class="nav-bottom"> or similar, wait.
    # Where are the links? I'll insert it right after the </svg></a> of settings.
    settings_regex = r'(<a href="/settings".*?</a>)'
    m = re.search(settings_regex, html, re.DOTALL)
    if m:
        html = html[:m.end()] + usuarios_btn + html[m.end():]
        print("Injected /usuarios anchor in inbox.html")
    
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(html)
