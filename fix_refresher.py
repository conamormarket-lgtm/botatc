import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = """                // Actualizar visibilidad de Chat
                const newScroll = doc.getElementById('chatScroll');
                const oldScroll = document.getElementById('chatScroll');
                if (newScroll && oldScroll) {
                    if (oldScroll.innerHTML !== newScroll.innerHTML) {
                        // Respetar scroll solo si el usuario no ha subido a leer
                        const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
                        oldScroll.innerHTML = newScroll.innerHTML;
                        if (isAtBottom) {
                            oldScroll.scrollTop = oldScroll.scrollHeight;
                        }
                    }
                }"""

rep = """                // Actualizar visibilidad de Chat
                const newScroll = doc.getElementById('chatScroll');
                const oldScroll = document.getElementById('chatScroll');
                if (newScroll && oldScroll) {
                    const isAtBottom = (oldScroll.scrollHeight - oldScroll.scrollTop) <= (oldScroll.clientHeight + 50);
                    let didAppend = false;
                    
                    const cleanHTML = (html) => html.replace(/style="[^"]*"/g, "").replace(/>\d+:\d{2}</g, ">0:00<");
                    
                    const newChildren = Array.from(newScroll.children);
                    
                    for (let i = 0; i < newChildren.length; i++) {
                        const newNode = newChildren[i];
                        const oldNode = oldScroll.children[i];
                        
                        if (!oldNode) {
                            oldScroll.appendChild(newNode.cloneNode(true));
                            didAppend = true;
                        } else {
                            if (cleanHTML(oldNode.innerHTML) !== cleanHTML(newNode.innerHTML)) {
                                const audio = oldNode.querySelector('audio');
                                if (audio && window._currentAudio === audio && !audio.paused) {
                                    continue;
                                }
                                oldScroll.replaceChild(newNode.cloneNode(true), oldNode);
                            }
                        }
                    }
                    
                    while (oldScroll.children.length > newChildren.length) {
                        oldScroll.removeChild(oldScroll.lastChild);
                    }
                    
                    if (didAppend && isAtBottom) {
                        oldScroll.scrollTop = oldScroll.scrollHeight;
                    }
                }"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced Refresher Logic")
else:
    print("Refresher logic not found!")
