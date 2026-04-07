import re

text = open('inbox.html', 'r', encoding='utf-8').read()

# Remove all skeleton CSS
text = re.sub(r'\s*\.skeleton \{.*?\n\s*\}\s*@keyframes skeleton-loading \{.*?\n\s*\}\s*', '', text, flags=re.DOTALL)

# Remove all injected scripts
text = re.sub(r'\s*// --- NAVEGACIÓN Y SKELETONS ---.*?\}\);\s*', '', text, flags=re.DOTALL)

# Add just the simple ESC logic right before the last </script> if it's not there
simple_logic = '''
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

# ensure only one insertion
idx = text.rfind('</script>')
if idx != -1:
    text = text[:idx] + simple_logic + '\n' + text[idx:]

open('inbox.html', 'w', encoding='utf-8').write(text)
print("Cleaned and fixed.")
