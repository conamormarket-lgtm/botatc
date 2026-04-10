import sys
with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('class="nav-item" title="Panel Clásico Anterior">')
end_a = text.find('</a>', idx) + 4

logout_btn = """
        <!-- Logout Icon -->
        <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-top: auto; color: #ef4444;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
        </a>
"""

text = text[:end_a] + logout_btn + text[end_a:]

with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added logout button")
