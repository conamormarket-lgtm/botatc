# ============================================================
#  firebase_client.py — Consultas a Firestore con Admin SDK
# ============================================================
import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_JSON, COLECCION_PEDIDOS


def inicializar_firebase():
    """Inicializa Firebase Admin una sola vez."""
    if not firebase_admin._apps:
        if FIREBASE_JSON:
            import json
            try:
                cred_dict = json.loads(FIREBASE_JSON)
                cred = credentials.Certificate(cred_dict)
            except Exception as e:
                raise ValueError(f"❌ Error parseando FIREBASE_JSON: {e}")
        else:
            if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"\n❌ No se encontró '{FIREBASE_CREDENTIALS_PATH}' ni la variable FIREBASE_JSON.\n"
                    "Genera la clave en Firebase Console → Configuración → Cuentas de servicio.\n"
                )
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            
        firebase_admin.initialize_app(cred)
    return firestore.client()


def _buscar(db, campo: str, valor: str) -> dict | None:
    """Busca un pedido por campo=valor. Sintaxis moderna de Firestore."""
    docs = (
        db.collection(COLECCION_PEDIDOS)
          .where(filter=FieldFilter(campo, "==", valor))
          .limit(1)
          .get()
    )
    for doc in docs:
        return doc.to_dict()
    return None


def buscar_pedido_por_telefono(telefono: str) -> list[dict]:
    """
    Busca por número de teléfono en clienteContacto tolerando espacios
    extraños introducidos manualmente desde el panel de control.
    """
    db = inicializar_firebase()

    # 1. Limpiar lo que escribió el cliente → solo dígitos
    digitos = telefono.replace(" ", "").replace("-", "").replace("+", "")

    # Quitar código de país peruano si viene incluido (51XXXXXXXXX)
    if digitos.startswith("51") and len(digitos) == 11:
        digitos = digitos[2:]

    # 2. Generar ambos formatos de búsqueda
    con_espacios = f"{digitos[:3]} {digitos[3:6]} {digitos[6:]}"  # '945 257 117'

    # 3. Cubrir posibles espacios accidentales en ambos polos (Firebase es exacto)
    variantes_busqueda = [
        digitos,
        f" {digitos}",
        f"{digitos} ",
        f" {digitos} ",
        con_espacios,
        f" {con_espacios}",
        f"{con_espacios} ",
        f" {con_espacios} "
    ]

    docs = (
        db.collection(COLECCION_PEDIDOS)
          .where(filter=FieldFilter("clienteContacto", "in", variantes_busqueda))
          .limit(20)
          .get()
    )
    
    resultados = []
    for doc in docs:
        resultados.append(doc.to_dict())
        
    # Ordenar los resultados localmente en memoria (por el campo 'id' descendente)
    # Ya que los IDs son secuenciales (006979, 008917...), el mayor es el más reciente.
    resultados.sort(key=lambda x: str(x.get("id", "0")), reverse=True)
    
    # Devolver únicamente los 5 pedidos más recientes para no saturar a la IA
    return resultados[:5]


def buscar_pedido_por_id(numero_pedido: str) -> dict | None:
    """
    Busca por N° de pedido (campo id).
    Firebase guarda IDs siempre con 6 dígitos y ceros a la izquierda
    (ej: '007053', '000001'). Se normaliza automáticamente.
    """
    db = inicializar_firebase()

    try:
        numero_normalizado = str(int(numero_pedido)).zfill(6)  # '7053' → '007053'
    except ValueError:
        numero_normalizado = numero_pedido

    variantes = list(dict.fromkeys([numero_normalizado, numero_pedido]))

    for variante in variantes:
        resultado = _buscar(db, "id", variante)
        if resultado:
            return resultado

    return None

# ============================================================
#  PERSISTENCIA DE CHATS (NUEVO)
# ============================================================

def guardar_sesion_chat(numero_wa: str, sesion_dict: dict):
    """Guarda toda la sesión del cliente en Firestore."""
    db = inicializar_firebase()
    doc_ref = db.collection("chats_atc").document(numero_wa)
    
    # Preparamos el dict para guardar
    data_to_save = {
        "bot_activo": sesion_dict.get("bot_activo", True),
        "ultima_actividad": sesion_dict.get("ultima_actividad"), # datetime object
        "escalado_en": sesion_dict.get("escalado_en"),           # datetime object o None
        "motivo_escalacion": sesion_dict.get("motivo_escalacion"),
        "nombre_cliente": sesion_dict.get("nombre_cliente", "Cliente"),
        "historial": sesion_dict.get("historial", []),
        "datos_pedido": sesion_dict.get("datos_pedido"),
        "pedidos_multiples": sesion_dict.get("pedidos_multiples"),
        "esperando_pedido_tester": sesion_dict.get("esperando_pedido_tester", False)
    }
    
    # Firestore maneja datetimes nativamente
    doc_ref.set(data_to_save)


def cargar_sesion_chat(numero_wa: str) -> dict | None:
    """Carga y devuelve la sesión si existe en Firestore."""
    db = inicializar_firebase()
    doc_ref = db.collection("chats_atc").document(numero_wa)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        # Aseguramos de que todo lo necesario esté para compatibilidad con la app local
        # Firestore devuelve Datetimes de google.api.core.datetime_helpers,
        # lo convertimos o lo dejamos, usualmente FastAPI/Python lo maneja bien si es naive/aware
        
        # Convertimos DatetimeWithNanoseconds a datetime ingenuo para evitar conflictos de zona horaria con datetime.utcnow()
        if data.get("ultima_actividad"):
            from google.api_core.datetime_helpers import DatetimeWithNanoseconds
            if isinstance(data["ultima_actividad"], DatetimeWithNanoseconds):
                data["ultima_actividad"] = data["ultima_actividad"].replace(tzinfo=None)
                
        if data.get("escalado_en"):
            from google.api_core.datetime_helpers import DatetimeWithNanoseconds
            if isinstance(data["escalado_en"], DatetimeWithNanoseconds):
                data["escalado_en"] = data["escalado_en"].replace(tzinfo=None)
                
        return data
    return None
