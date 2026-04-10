import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

idx1=text.find('<form onsubmit="window.enviarMensajeManual')
idx2=text.find('</form>', idx1)
print(text[idx1:idx2+7])
