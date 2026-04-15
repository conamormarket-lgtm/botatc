import firebase_admin
from firebase_admin import credentials, firestore
import json

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

qrs = db.collection("bot_quick_replies").stream()
out = []
for q in qrs:
    out.append(q.to_dict())

print(json.dumps(out, indent=2, ensure_ascii=False))
