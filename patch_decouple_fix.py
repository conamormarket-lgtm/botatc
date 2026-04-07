import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# We need to replace the btn.click() logic inside the loop!

pattern = r'const endsWithSlash[^;]+;\s*input\.value =[^;]+;\s*if\s*\(btn\)\s*btn\.click\(\);'

new_logic = '''if (window.enviarMensajeDirecto) {
                        await window.enviarMensajeDirecto("{wa_id}", finalMsg);
                    } else {
                        const endsWithSlash = input.value.trimEnd().endsWith("/");
                        input.value = (endsWithSlash && i===0) ? input.value.trimEnd().slice(0,-1) + finalMsg : finalMsg;
                        if(btn) btn.click();
                    }'''

if 'window.enviarMensajeDirecto' not in text:
    new_text = re.sub(pattern, new_logic, text)
    if new_text != text:
        with open('server.py', 'w', encoding='utf-8') as f:
            f.write(new_text)
        print("Successfully decoupled logic in server.py")
    else:
        print("Regex did not match!")
else:
    print("Already fixed")
