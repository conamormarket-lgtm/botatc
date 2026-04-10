import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""        // Escuchar input manual
        document.addEventListener('input', function(e) {
            if(e.target.id === 'manualMsgInput') {
                window.toggleSendMicButton();
            }
        });"""

rep = r"""        // Escuchar input manual
        document.addEventListener('input', function(e) {
            if(e.target.id === 'manualMsgInput') {
                window.toggleSendMicButton();
            }
        });
        
        // Interceptar asignaciones programáticas a value
        const originalValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        setTimeout(() => {
            const msgInput = document.getElementById('manualMsgInput');
            if (msgInput && msgInput.__valueInterceptor !== true) {
                Object.defineProperty(msgInput, "value", {
                    set: function(val) {
                        originalValueSetter.call(this, val);
                        if (window.toggleSendMicButton) window.toggleSendMicButton();
                    },
                    get: function() {
                        return Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").get.call(this);
                    }
                });
                msgInput.__valueInterceptor = true;
                if(window.toggleSendMicButton) window.toggleSendMicButton();
            }
        }, 1000); // Darle tiempo a la creacion del SPA"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Added input setter interceptor")
else:
    print("Not found interceptor target")
