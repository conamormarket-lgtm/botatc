# ============================================================
#  document_loader.py — Carga archivos de guía al system prompt
#  Soporta: .md, .txt, .pdf
# ============================================================
import os
from pypdf import PdfReader


def _leer_txt_md(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as f:
        return f.read().strip()


def _leer_pdf(ruta: str) -> str:
    reader = PdfReader(ruta)
    paginas = []
    for i, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text()
        if texto and texto.strip():
            paginas.append(f"[Página {i}]\n{texto.strip()}")
    return "\n\n".join(paginas)


def cargar_documento(ruta: str, etiqueta: str = None) -> str:
    """
    Carga un archivo de guía y retorna su contenido como texto.
    Soporta .md, .txt y .pdf.

    Args:
        ruta:     Ruta al archivo.
        etiqueta: Nombre descriptivo para mostrar en consola (opcional).

    Returns:
        Contenido del documento como string, o "" si no existe.
    """
    nombre = etiqueta or os.path.basename(ruta)

    if not os.path.exists(ruta):
        print(f"⚠️  '{nombre}' no encontrado en '{ruta}'. Se omitirá.")
        return ""

    extension = os.path.splitext(ruta)[1].lower()

    try:
        if extension == ".pdf":
            contenido = _leer_pdf(ruta)
        elif extension in (".md", ".txt"):
            contenido = _leer_txt_md(ruta)
        else:
            print(f"⚠️  Formato '{extension}' no soportado para '{nombre}'. Usa .pdf, .md o .txt.")
            return ""

        if not contenido.strip():
            print(f"⚠️  '{nombre}' está vacío o no se pudo extraer texto.")
            return ""

        chars = len(contenido)
        tokens_aprox = chars // 4  # ~4 caracteres por token en español
        print(f"📄 '{nombre}' cargado — {chars:,} caracteres (~{tokens_aprox:,} tokens).")
        return contenido

    except Exception as e:
        print(f"❌ Error al leer '{nombre}': {e}")
        return ""


def cargar_multiples(archivos: list[dict]) -> str:
    """
    Carga múltiples documentos y los une en un solo bloque de texto.

    Args:
        archivos: Lista de dicts con claves 'ruta' y opcionalmente 'etiqueta'.
                  Ejemplo:
                    [
                      {"ruta": "guia_respuestas.md",  "etiqueta": "Guía principal"},
                      {"ruta": "politicas.pdf",        "etiqueta": "Políticas de devolución"},
                    ]

    Returns:
        Todo el contenido unido, separado por bloques etiquetados.
    """
    bloques = []
    for item in archivos:
        ruta     = item.get("ruta", "")
        etiqueta = item.get("etiqueta", os.path.basename(ruta))
        contenido = cargar_documento(ruta, etiqueta)
        if contenido:
            bloques.append(f"=== {etiqueta.upper()} ===\n{contenido}\n=== FIN: {etiqueta.upper()} ===")

    return "\n\n".join(bloques)
