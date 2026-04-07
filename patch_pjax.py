import re

with open('server.py', 'r', encoding='utf-8') as f:
    s_text = f.read()

# Make isSendingSequence attach to window so it's globally detectable everywhere
if 'window.isSendingSequence = true;' not in s_text:
    s_text = s_text.replace('let isSendingSequence = false;', 'window.isSendingSequence = false;\n            let isSendingSequence = false;')
    s_text = s_text.replace('isSendingSequence = true;', 'isSendingSequence = true; window.isSendingSequence = true;')
    s_text = s_text.replace('isSendingSequence = false;', 'isSendingSequence = false; window.isSendingSequence = false;')
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(s_text)

with open('inbox.html', 'r', encoding='utf-8') as f:
    i_text = f.read()

pjax_code = '''
        // Intercept clicks on other chats if a sequence is sending
        document.addEventListener('click', async function(e) {
            const chatRow = e.target.closest('.chat-row');
            if (chatRow && window.isSendingSequence) {
                e.preventDefault();
                const url = chatRow.href;
                
                // Soft Navigation (PJAX style)
                window.history.pushState(null, '', url);
                document.querySelectorAll('.chat-row').forEach(row => row.classList.remove('active-row'));
                chatRow.classList.add('active-row');
                
                const viewer = document.querySelector('.chat-viewer-panel');
                if (viewer) {
                    viewer.innerHTML = '<div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100%; color:var(--text-muted);"><h3>Cargando chat en segundo plano...</h3></div>';
                    try {
                        const response = await fetch(url);
                        const html = await response.text();
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newViewer = doc.querySelector('.chat-viewer-panel');
                        if (newViewer) {
                            viewer.innerHTML = newViewer.innerHTML;
                        }
                    } catch(err) {
                        window.location.href = url; // Fallback
                    }
                }
            }
        });

        // Smart ESC to exit chat without interrupting sequence
'''

if 'Intercept clicks on other chats' not in i_text:
    i_text = i_text.replace('// Smart ESC to exit chat without interrupting sequence', pjax_code)
    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(i_text)
    print("PJAX and ESC logics updated")
else:
    print("Already updated inbox")
