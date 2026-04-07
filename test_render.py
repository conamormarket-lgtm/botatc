import server, fastapi
from datetime import datetime

r = fastapi.Request({'type': 'http', 'headers': []})
server.verificar_sesion = lambda req: True
server.sesiones['12'] = {
    'nombre': 'Test',
    'mensajes': [],
    'ultima_actividad': datetime.now(),
    'wa_id': '12',
    'etiquetas': []
}
html = server.renderizar_inbox(r, '12', 'all', '', False).body.decode()
open('dump.html', 'w', encoding='utf-8').write(html)
print('cargarQuickReplies in HTML:', 'cargarQuickReplies' in html)
print('rightSidebar in HTML:', 'rightSidebar' in html)
