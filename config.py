# ============================================================
#  config.py — Configuración centralizada del bot de ATC
#  Lee variables desde .env (local) o variables de Railway (producción)
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()  # carga .env si existe (desarrollo local)

# --- Archivos de guía del bot ---
import glob
DOCUMENTOS_GUIA = [{"ruta": "guia_respuestas.md", "etiqueta": "Guía de respuestas principal"}]

# Auto-descubrir cualquier PDF en la carpeta raíz
for pdf_file in glob.glob("*.pdf"):
    DOCUMENTOS_GUIA.append({"ruta": pdf_file, "etiqueta": pdf_file.replace(".pdf", "")})

# --- LM Studio (solo para bot_atc.py en consola) ---
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY  = "lm-studio"
LM_STUDIO_MODEL    = "local-model"

# --- Groq API (para server.py en producción) ---
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = "llama-3.1-8b-instant"

# --- Parámetros del modelo ---
TEMPERATURE = 0.05  # casi determinista: sigue los documentos sin inventar

# --- Meta WhatsApp Business API ---
META_ACCESS_TOKEN    = os.getenv("META_ACCESS_TOKEN", "")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
META_VERIFY_TOKEN    = os.getenv("META_VERIFY_TOKEN", "bot_atc_token")
META_API_VERSION     = "v19.0"

# --- Firebase ---
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
FIREBASE_JSON             = os.getenv("FIREBASE_JSON")
COLECCION_PEDIDOS         = "pedidos"

# --- Sesiones ---
MAX_HISTORIAL_TURNOS     = 20
SESION_EXPIRA_HORAS      = 4    # tras N horas de inactividad → sesión nueva
ESTADOS_DISEÑO           = {"En Diseño", "en diseño", "Diseño", "diseño"}

# --- Panel de administración ---
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")  # cambiar en producción

# --- Modo Tester (números que pueden probar con cualquier pedido) ---
NUMEROS_TESTER = {"997778512", "51997778512"}  # el dueño puede probar con N° de pedido manual
