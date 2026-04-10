import sys

with open("prompts.py", "r", encoding="utf-8") as f:
    text = f.read()

target = 'Tu canal de atención es WhatsApp exclusivamente.\\n\\nREGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:'
rep = 'Tu canal de atención es WhatsApp exclusivamente.\\n\\nREGLAS CRÍTICAS — SÍGUELAS SIN EXCEPCIÓN:\\n0. SIEMPRE debes referirte al cliente usando ÚNICAMENTE el "Nombre" de cliente que aparece adjunto en sus datos de pedido correspondiente. Abstente de usar otros apodos o nombres extraños que el usuario posea.'

if target in text:
    text = text.replace(target, rep)
    with open("prompts.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Replaced prompt rules for names")
else:
    print("Target not found")
