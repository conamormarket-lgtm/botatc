import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the Quick Replies sidebar/panel section — look for the button that loads quick replies
# or the panel-id for quick replies
patterns = ['panel-respuestas', 'sidebar-replies', 'panel-quick', 'quickReplyPanel', 'respuestasPanel',
            'tabQuick', 'btn-respuestas', 'loadQuickReplies', 'cargarRespuestasRapidas',
            'enviarMensajeRapido', 'sendQuickReply', 'enviarMensajesRapido',
            'wa_id.*quick', 'quick.*wa_id']
for p in patterns:
    idx = s.find(p)
    if idx != -1:
        print(f"=== '{p}' at {idx} ===")
        print(s[max(0,idx-50):idx+400])
        print()
