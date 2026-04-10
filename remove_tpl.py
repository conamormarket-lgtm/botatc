import sys
import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

# Removing the button:
# <div style="padding: 0 20px 10px 20px;">
#                 <button onclick="openTemplateModal()" class="dashboard-btn" style="width: 100%; background: var(--success-color); border:none; border-radius:10px; font-weight:600; cursor:pointer;">
#                     💬 Nueva Conversación
#                 </button>
#             </div>
text = re.sub(r'<div style="padding: 0 20px 10px 20px;">\s*<button onclick="openTemplateModal\(\)".*?</button>\s*</div>', '', text, flags=re.DOTALL)

# Removing the modal HTML
text = re.sub(r'<!-- Modal: Start Template Conversation -->.*?</div>\s*</div>', '', text, flags=re.DOTALL)

# Removing the JS
text = re.sub(r'function openTemplateModal\(\).*?btn\.disabled = false;\s*\}', '', text, flags=re.DOTALL)

with open("inbox.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Plantillas borradas de la UI")
