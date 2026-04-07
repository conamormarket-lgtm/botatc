import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

direct_js = '''
        window.enviarMensajeDirecto = async function(wa_id, msj) {
            if (!msj) return;
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : '';
            try {
                await fetch('/enviar_mensaje', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `wa_id=${wa_id}&mensaje=${encodeURIComponent(msj)}&reply_to=${replyToWamid}`
                });
            } catch(e) {
                console.error("Error direct send", e);
            }
        };

        window.enviarMensajeManual = async function (e, wa_id) {'''

if 'window.enviarMensajeDirecto =' not in text:
    text = text.replace('window.enviarMensajeManual = async function (e, wa_id) {', direct_js)
    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("enviarMensajeDirecto added to inbox.html")
else:
    print("enviarMensajeDirecto already exists")

with open('server.py', 'r', encoding='utf-8') as f:
    s_text = f.read()

old_loop_logic = '''
                    const endsWithSlash = input.value.trimEnd().endsWith("/");
                    input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;

                    if(btn) btn.click();
'''

new_loop_logic = '''
                    if (window.enviarMensajeDirecto) {
                        await window.enviarMensajeDirecto("{wa_id}", finalMsg);
                    } else {
                        const endsWithSlash = input.value.trimEnd().endsWith("/");
                        input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
                        if(btn) btn.click();
                    }
'''

if 'window.enviarMensajeDirecto' not in s_text:
    s_text = s_text.replace(old_loop_logic, new_loop_logic)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(s_text)
    print("server.py loop updated")
else:
    print("server.py loop already updated")
