import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find where a quick reply triggers sending
# Quick replies list: look for .title, .content for qr objects
patterns = ['qr\.title', 'qr\.content', 'reply\.title', 'r\.title', 'r\.content', 
            'enviar_manual.*quick', 'quick.*enviar',
            'aplicarRespuesta', 'usarRespuesta', 'sendQuick', 'seleccionarRespuesta',
            'replyTitle', 'quickReplyTitle']
found = False
for p in patterns:
    matches = [m.start() for m in re.finditer(p, s, re.IGNORECASE)]
    if matches:
        found = True
        print(f"=== '{p}' ===")
        print(s[max(0, matches[0]-100):matches[0]+300])
        print()

if not found:
    # look at all quick-reply related buttons/clicks
    idx = s.find('quick-repl')
    if idx == -1:
        idx = s.find('quickRepl')
    print(f"idx={idx}")
    print(s[max(0,idx-100):idx+600])
