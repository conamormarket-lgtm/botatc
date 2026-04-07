import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad_js = '''if (window.enviarMensajeDirecto) {
                        await window.enviarMensajeDirecto("{wa_id}", finalMsg);
                    } else {
                        const endsWithSlash = input.value.trimEnd().endsWith("/");
                        input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
                        if(btn) btn.click();
                    }'''

good_js = '''if (window.enviarMensajeDirecto) {{
                        await window.enviarMensajeDirecto("{wa_id}", finalMsg);
                    }} else {{
                        const endsWithSlash = input.value.trimEnd().endsWith("/");
                        input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
                        if(btn) btn.click();
                    }}'''

if bad_js in text:
    text = text.replace(bad_js, good_js)
    with open('server.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed f-string syntax in server.py")
else:
    print("Could not find the bad js")
