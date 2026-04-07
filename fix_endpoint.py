import re

with open('inbox.html', 'r', encoding='utf-8') as f:
    text = f.read()

bad_js = '''window.enviarMensajeDirecto = async function(wa_id, msj) {
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
        };'''

good_js = '''window.enviarMensajeDirecto = async function(wa_id, msj) {
            if (!msj) return;
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            try {
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
                });
                
                const data = await res.json();
                if(!data.ok) { console.error("Error direct send json", data); }
            } catch(e) {
                console.error("Error direct send", e);
            }
        };'''

if 'fetch(\'/enviar_mensaje\'' in text:
    text = text.replace(bad_js, good_js)
    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed fetch endpoint in inbox.html")
else:
    print("Not found")
