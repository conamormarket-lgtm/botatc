import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find where quick reply is applied and text sent
patterns = ['quick', 'respuesta.*r', 'qr.content', 'qr.title', 'reply.title', 'enviarRespuestaRapida']
for p in patterns:
    matches = [m.start() for m in re.finditer(p, s, re.IGNORECASE)]
    if matches:
        print(f"=== '{p}' ({len(matches)} matches) ===")
        print(s[max(0, matches[0]-50):matches[0]+200])
        print()
