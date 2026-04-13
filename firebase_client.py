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
        "esperando_pedido_tester": sesion_dict.get("esperando_pedido_tester", False),
        "etiquetas": sesion_dict.get("etiquetas", [])
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

def cargar_todas_las_sesiones() -> dict:
    """Carga TODAS las sesiones de Firestore para poblar la RAM en el arranque del servidor."""
    db = inicializar_firebase()
    coleccion = db.collection("chats_atc")
    docs = coleccion.stream()
    
    sesiones_restauradas = {}
    from google.api_core.datetime_helpers import DatetimeWithNanoseconds
    
    for doc in docs:
        data = doc.to_dict()
        if data.get("ultima_actividad") and isinstance(data["ultima_actividad"], DatetimeWithNanoseconds):
            data["ultima_actividad"] = data["ultima_actividad"].replace(tzinfo=None)
        if data.get("escalado_en") and isinstance(data["escalado_en"], DatetimeWithNanoseconds):
            data["escalado_en"] = data["escalado_en"].replace(tzinfo=None)
        sesiones_restauradas[doc.id] = data
        
    return sesiones_restauradas

# ============================================================
#  PERSISTENCIA DE STICKERS EN FIRESTORE
# ============================================================
import base64

def guardar_sticker_en_bd(filename: str, file_bytes: bytes):
    """Guarda físicamente un archivo en la base de datos convirtiéndolo a Base64."""
    db = inicializar_firebase()
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    db.collection("bot_stickers").document(filename).set({
        "filename": filename,
        "base64": b64_data,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })

def obtener_sticker_de_bd(filename: str) -> bytes | None:
    """Recupera un sticker individual decodificado desde Firestore."""
    db = inicializar_firebase()
    doc = db.collection("bot_stickers").document(filename).get()
    if doc.exists:
        data = doc.to_dict()
        b64 = data.get("base64")
        if b64:
            return base64.b64decode(b64)
    return None

def obtener_todos_los_nombres_stickers() -> list[str]:
    """Devuelve solo los nombres de archivo de los stickers para listar en la UI sin descargar los bytes."""
    db = inicializar_firebase()
    docs = db.collection("bot_stickers").select(["filename"]).limit(300).stream()
    return [doc.to_dict().get("filename") for doc in docs if doc.to_dict().get("filename")]

# ============================================================
#  PERSISTENCIA DE WALLPAPERS EN FIRESTORE
# ============================================================

def guardar_wallpaper_en_bd(filename: str, file_bytes: bytes, ext: str):
    """Guarda un wallpaper en la base de datos convirtiéndolo a Base64."""
    db = inicializar_firebase()
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    db.collection("bot_wallpapers").document(filename).set({
        "filename": filename,
        "extension": ext,
        "base64": b64_data,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })

def obtener_wallpaper_de_bd(filename: str) -> bytes | None:
    """Recupera un wallpaper devuelto como bytes decodificados."""
    db = inicializar_firebase()
    doc = db.collection("bot_wallpapers").document(filename).get()
    if doc.exists:
        data = doc.to_dict()
        b64 = data.get("base64")
        if b64:
            return base64.b64decode(b64)
    return None


# ============================================================
#  PERSISTENCIA DE PLANTILLAS EN FIRESTORE
# ============================================================

def guardar_plantilla_bd(nombre: str, idioma: str = "es"):
    db = inicializar_firebase()
    db.collection("bot_templates").document(nombre).set({
        "name": nombre,
        "language": idioma,
        "createdAt": firestore.SERVER_TIMESTAMP
    })

def eliminar_plantilla_bd(nombre: str):
    db = inicializar_firebase()
    db.collection("bot_templates").document(nombre).delete()

def cargar_plantillas_bd() -> list:
    db = inicializar_firebase()
    docs = db.collection("bot_templates").stream()
    plantillas = []
    for doc in docs:
        data = doc.to_dict()
        if "name" in data:
            plantillas.append(data)
    return plantillas


# ============================================================
#  PERSISTENCIA DE ETIQUETAS GLOBALES (LABELS)
# ============================================================

def guardar_etiqueta_bd(id_etiqueta: str, nombre: str, color: str):
    db = inicializar_firebase()
    db.collection("bot_labels").document(id_etiqueta).set({
        "id": id_etiqueta,
        "name": nombre,
        "color": color,
        "createdAt": firestore.SERVER_TIMESTAMP
    })

def eliminar_etiqueta_bd(id_etiqueta: str):
    db = inicializar_firebase()
    db.collection("bot_labels").document(id_etiqueta).delete()

def cargar_etiquetas_bd() -> list:
    db = inicializar_firebase()
    docs = db.collection("bot_labels").stream()
    etiquetas = []
    for doc in docs:
        data = doc.to_dict()
        if "id" in data:
            etiquetas.append(data)
    return etiquetas


# ============================================================
#  PERSISTENCIA DE RESPUESTAS RÁPIDAS (QUICK REPLIES)
# ============================================================

def guardar_quick_reply_bd(id_qr: str, titulo: str, contenido: str, categoria: str = "General", tipo: str = "text", mensajes: list = None, delay_ms: int = 1500, etiquetas: list = None):
    db = inicializar_firebase()
    
    data = {
        "id": id_qr,
        "title": titulo,
        "content": contenido,
        "category": categoria,
        "type": tipo,
        "delay_ms": delay_ms,
        "etiquetas": etiquetas if etiquetas is not None else []
    }
    if mensajes is not None:
        data["mensajes"] = mensajes
    else:
        data["mensajes"] = [{"type": "text", "content": contenido}] if contenido else []
        
    data["createdAt"] = firestore.SERVER_TIMESTAMP
    db.collection("bot_quick_replies").document(id_qr).set(data, merge=True)

def eliminar_quick_reply_bd(id_qr: str):
    db = inicializar_firebase()
    db.collection("bot_quick_replies").document(id_qr).delete()

def cargar_quick_replies_bd() -> list:
    db = inicializar_firebase()
    docs = db.collection("bot_quick_replies").stream()
    qrs = []
    for doc in docs:
        data = doc.to_dict()
        if "id" in data:
            # Normalize mensajes: convert old string-only format to objects
            mensajes = data.get("mensajes", [])
            normalized = []
            for m in mensajes:
                if isinstance(m, str):
                    normalized.append({"type": "text", "content": m})
                else:
                    normalized.append(m)
            data["mensajes"] = normalized
            # Ensure etiquetas field exists
            data.setdefault("etiquetas", [])
            qrs.append(data)
    return qrs

def guardar_grupo_bd(grupo: dict):
    db = inicializar_firebase()
    if db: db.collection("virtual_groups").document(grupo["id"]).set(grupo)

def eliminar_grupo_bd(grupo_id: str):
    db = inicializar_firebase()
    if db: db.collection("virtual_groups").document(grupo_id).delete()

def cargar_grupos_bd() -> list:
    db = inicializar_firebase()
    if not db: return []
    docs = db.collection("virtual_groups").stream()
    return [d.to_dict() for d in docs]


# ─────────────────────────────────────────────
#  USER AUTENTICATION AND MANAGEMENT
# ─────────────────────────────────────────────

def crear_usuario(username: str, password_hash: str) -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        return False
    doc_ref.set({
        "password": password_hash,
        "estado": "pendiente",
        "permisos": []
    })
    return True

def obtener_usuario(username: str) -> dict | None:
    db = inicializar_firebase()
    doc = db.collection("usuarios_atc").document(username).get()
    if doc.exists:
        data = doc.to_dict()
        data["username"] = username
        return data
    return None

def obtener_todos_los_usuarios() -> list[dict]:
    db = inicializar_firebase()
    docs = db.collection("usuarios_atc").get()
    res = []
    for doc in docs:
        d = doc.to_dict()
        d["username"] = doc.id
        res.append(d)
    return res

def actualizar_permisos_usuario(username: str, estado: str, permisos: list[str], nombre: str = "") -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        update_data = {
            "estado": estado,
            "permisos": permisos
        }
        if nombre:
            update_data["nombre"] = nombre
        doc_ref.update(update_data)
        return True
    return False

def actualizar_preferencias_tema(username: str, preferencias_ui: dict) -> bool:
    db = inicializar_firebase()
    doc_ref = db.collection("usuarios_atc").document(username)
    if doc_ref.get().exists:
        doc_ref.update({"preferencias_ui": preferencias_ui})
        return True
    return False
