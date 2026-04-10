import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('enviarMensajeManual')
if idx != -1:
    print(text[max(0, idx-500):idx+500])
else:
    print("Not found")
