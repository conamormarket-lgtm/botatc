import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = """        const chatsContainerDiv = document.getElementById('regularChatsContainer');
        if (chatsContainerDiv) {
            const savedScroll = sessionStorage.getItem('chatListScrollTop');
            if (savedScroll) {
                setTimeout(() => { chatsContainerDiv.scrollTop = parseInt(savedScroll); }, 50);
            }
            chatsContainerDiv.addEventListener('scroll', function() {
                sessionStorage.setItem('chatListScrollTop', this.scrollTop);
            });
        }"""

rep = """        const chatsContainerDiv = document.getElementById('regularChatsContainer');
        if (chatsContainerDiv) {
            const applyScroll = () => {
                const s = sessionStorage.getItem('chatListScrollTop');
                if (s) chatsContainerDiv.scrollTop = parseInt(s);
            };
            
            // Apply immediately, and firmly a few times to beat browser rendering or filter passes
            applyScroll();
            setTimeout(applyScroll, 50);
            setTimeout(applyScroll, 150);
            setTimeout(applyScroll, 300);

            // Record cleanly using event listener, throttled/debounced implicitly? 
            chatsContainerDiv.addEventListener('scroll', function() {
                sessionStorage.setItem('chatListScrollTop', this.scrollTop);
            });

            // Adicionalmente, asegurar que si se hace clic en un chat, se guarde justo ese instante
            const chatLinks = chatsContainerDiv.querySelectorAll('.chat-row');
            chatLinks.forEach(link => {
                link.addEventListener('click', () => {
                    sessionStorage.setItem('chatListScrollTop', chatsContainerDiv.scrollTop);
                });
            });
        }"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected robust scroll restorer!")
else:
    print("Target not found inbox.html!")
