import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find('<form onsubmit="window.enviarMensajeManual')
idx2 = text.find('</form>', idx)
print(text[idx:idx2+10])
