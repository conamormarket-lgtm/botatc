import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the quick reply section - look for where quick replies build the button list
patterns = ['rr.title', 'qr.title', '.title', 'manualMsgInput.*value', 'input.*value.*=.*r']
# Look for assignment of quick reply text to the input
idx = s.find('enviarRespuestasRapidas')
if idx == -1:
    idx = s.find('usarRespuestaRapida')
if idx == -1:
    # Look for where r.title or r.content is used in the context of replies
    idx = s.find('r.title')
if idx == -1:
    idx = s.find('.title')
    
print(f"idx={idx}")
print(s[max(0,idx-50):idx+600])
