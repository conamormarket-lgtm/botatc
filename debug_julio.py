
import firebase_client
from datetime import datetime
db = firebase_client.inicializar_firebase()
rules = firebase_client.cargar_followup_rules_bd()

d = db.collection('chats_atc').document('51977756262').get()
if d.exists:
    sesion = d.to_dict()
    ua = sesion.get('ultima_actividad')
    if ua:
        ua_ts = ua.timestamp()
        sesion['ultima_actividad'] = datetime.utcfromtimestamp(ua_ts)
        
    now = datetime.utcnow()
    horas_inactivo = (now - sesion['ultima_actividad']).total_seconds() / 3600
    print('Horas inactivo reales (UTC corregido):', horas_inactivo)
    
    for rule in rules:
        if not rule.get('activo'): continue
        
        rule_line = rule.get('line_id', 'todas')
        sesion_line = sesion.get('lineId', 'principal')
        
        print('Eval Rule', rule.get('nombre'), 'rule_line=', rule_line, 'sesion_line=', sesion_line)
        
        if rule_line != 'todas' and rule_line != sesion_line:
            print('-> FAILED: Line mismatch')
            continue
            
        if rule['id'] in sesion.get('seguimientos_enviados', []):
            print('-> FAILED: Already sent')
            continue
            
        if horas_inactivo >= rule.get('horas_inactividad', 23):
            print('-> SUCCESS: WOULD TRIGGER!')
        else:
            print('-> FAILED: Not enough hours (Needs', rule.get('horas_inactividad'), ')')

