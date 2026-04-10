import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Quick replies are shown in a panel. Let's find the panel button onclick
# or the function that handles clicking on a quick reply
patterns = [
    'quick_repl',  # snake case
    'quickRepl',   # camel case  
    'respuesta_r', 
    'RespuestaR',
    'rapida',
    'aplicar',
    'btn-reply',
    'tab-reply',
    '/api/quick',
]
for p in patterns:
    idx = s.find(p)
    if idx != -1:
        print(f"=== '{p}' at {idx} ===")
        print(s[max(0,idx-100):idx+500])
        print()
