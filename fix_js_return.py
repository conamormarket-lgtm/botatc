import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old_func_start = "window.enviarMensajeDirecto = async function"
old_func_end = "};"

# Let's cleanly replace the entire window.enviarMensajeDirecto function
pattern = r"window\.enviarMensajeDirecto\s*=\s*async\s*function\s*\(\s*wa_id,\s*msj\s*\)\s*\{.*?(?=\n\s*window\.enviarMensajeManual)"
match = re.search(pattern, text, re.DOTALL)

new_func = '''window.enviarMensajeDirecto = async function(wa_id, msj) {
            if (!msj) return {ok: false};
            const replyToWamid = document.getElementById('replyToWamid') ? document.getElementById('replyToWamid').value : null;
            try {
                const res = await fetch('/api/admin/enviar_manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ wa_id: wa_id, texto: msj, reply_to_wamid: replyToWamid })
                });

                const data = await res.json();
                if(!data.ok) { console.error("Error direct send json", data); }
                return data;
            } catch(e) {
                console.error("Error direct send", e);
                return {ok: false, error: e.message || "Red Error"};
            }
        };'''

if match:
    text = text[:match.start()] + new_func + text[match.end():]
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed JS return issue")
else:
    print("Could not find function to replace")
