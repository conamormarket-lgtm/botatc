import sys
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Quitar el logout anterior si existe en la mitad de la sidebar
text = re.sub(r'<!-- Logout Icon -->.*?</a>', '', text, flags=re.DOTALL)

rep = """
        <!-- Logout Button (reemplazando al dot) -->
        <a href="/logout" class="nav-item" title="Cerrar Sesión" style="margin-top: auto; margin-bottom: 20px; color: #ef4444; display: flex; justify-content: center; text-decoration: none;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 28px; height: 28px; opacity: 0.8; transition: opacity 0.2s;">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
        </a>
"""

text = re.sub(r'<!-- Indicador global abajo -->\s*<div class="bot-status-indicator" title="Estado Global del Bot"></div>', rep, text)

# By the way, wait, bot-status-indicator is used in JS to show if bot is connected!
# "quitar el punto verde de la esquina inferior izquierda" -> user explicitly said to remove the green dot.
# I will make sure the JS doesn't crash if it cannot find `.bot-status-indicator`.
text = re.sub(r"document\.querySelector\('\.bot-status-indicator'\)\.classList\.remove\(.*?\);", '', text)
text = re.sub(r"document\.querySelector\('\.bot-status-indicator'\)\.classList\.add\(.*?\);", '', text)
text = re.sub(r"const globalBot = document\.querySelector\('\.bot-status-indicator'\);", "const globalBot = null;", text)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Quitado punto verde y agregado Logout abajo")
