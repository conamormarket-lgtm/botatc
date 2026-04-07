import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix sidebar-nav
text = re.sub(r'(\.sidebar-nav\s*\{[^}]+?)background-color:\s*var\(--bg-main\);([^}]+\})', r'\1background-color: var(--bg-sidebar);\2', text)
text = re.sub(r'\s*background-color:\s*var\(--bg-list\);\s*\}', '\n        }', text)
text = re.sub(r'\s*background-color:\s*var\(--bg-sidebar\);\s*\}', '\n        }', text)

# Fix chat-list-panel
text = re.sub(r'(\.chat-list-panel\s*\{[^}]+?)background-color:\s*var\(--bg-main\);([^}]+\})', r'\1background-color: var(--bg-list);\2', text)

with open('inbox.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
