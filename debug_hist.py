import sys, json
sys.path.append('.')
from firebase_client import inicializar_firebase
db = inicializar_firebase()
doc = db.collection('chats_atc').document('51997778512').get()
if doc.exists:
    historial = doc.to_dict().get('historial', [])
    for h in historial[-5:]:
        # safe print using ascii representation to avoid powershell unicode errors
        print(repr(f"{h.get('timestamp')}: {h.get('role')} - {h.get('content')} - {h.get('sent_by', 'user')}"))
