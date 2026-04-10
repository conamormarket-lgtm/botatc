import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Look for where quick reply sends — the function that sends multiple messages from a QR
# Quick replies have multi-message sequences. Find where they are sent
for pattern in ['mensajes', 'delay_ms', 'cargar.*quick', 'cargarRespuestas']:
    matches = [m.start() for m in re.finditer(pattern, s, re.IGNORECASE)]
    if matches:
        print(f"=== '{pattern}' ({len(matches)}) ===")
        print(s[max(0,matches[0]-50):matches[0]+400])
        print()
        break
