import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update recibir_mensaje document handler
target_doc = r'elif tipo_mensaje == "document":\s+filename = mensaje_data\.get\("document", \{\}\)\.get\("filename", "documento"\)\s+texto_cliente = f"\[[^\n]+Archivo: \{filename\}\]"'
replacement_doc = r"""elif tipo_mensaje == "document":
            filename = mensaje_data.get("document", {}).get("filename", "documento")
            media_id = mensaje_data.get("document", {}).get("id", "")
            texto_cliente = f"[documento:{media_id}|{filename}]" """

if re.search(target_doc, text):
    text = re.sub(target_doc, replacement_doc, text)
    print("Updated document ingestion")
else:
    print("Cannot find target_doc")

# 2. Update reemplazar_archivos_inline to handle documento
target_render = r'texto_renderizado = re\.sub\(r"\\\[\(sticker-local\|sticker\|imagen\|audio\|video\):([^\]]+)\\\]", reemplazar_archivos_inline, texto\)'
replacement_render = r'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video|documento):([^\]]+)\]", reemplazar_archivos_inline, texto)'
text = re.sub(r'texto_renderizado\s*=\s*re\.sub\(r\"\\\[\(sticker-local\|sticker\|imagen\|audio\|video\):\(\[\^\\\]\]\+\)\\\]\",\s*reemplazar_archivos_inline,\s*texto\)',
              r'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video|documento):([^\]]+)\]", reemplazar_archivos_inline, texto)', text)

# Just literal replacement
if r'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video):([^\]]+)\]", reemplazar_archivos_inline, texto)' in text:
    text = text.replace(r'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video):([^\]]+)\]", reemplazar_archivos_inline, texto)',
                        r'texto_renderizado = re.sub(r"\[(sticker-local|sticker|imagen|audio|video|documento):([^\]]+)\]", reemplazar_archivos_inline, texto)')
    print("Replaced regex in renderizar_inbox")

# 3. Add `elif tipo == "documento":`
target_audio = r'elif tipo == "audio":\s+return f\'<div style="text-align:center;"><audio controls src="\{src_url\}" style="max-width: 250px; height: 40px; outline: none; margin-bottom: 5px;"></audio></div>\''
replacement_audio = r"""elif tipo == "audio":
                    return f'<div style="text-align:center;"><audio controls src="{src_url}" style="max-width: 250px; height: 40px; outline: none; margin-bottom: 5px;"></audio></div>'
                elif tipo == "documento":
                    partes = media_id.split("|", 1)
                    doc_id = partes[0]
                    doc_name = partes[1] if len(partes) > 1 else "Documento"
                    doc_url = f"/api/media/{doc_id}"
                    return f'<div style="margin-bottom: 5px;"><a href="{doc_url}" download="{doc_name}" target="_blank" style="display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; text-decoration: none; color: inherit; font-size: 0.9rem; border: 1px solid var(--accent-border);">📎 {doc_name} <span style="font-size:0.8rem; margin-left:auto; opacity:0.6;">📥 Bajar</span></a></div>'"""

if re.search(target_audio, text):
    text = re.sub(target_audio, replacement_audio, text)
    print("Added document to render")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
    
print("Document download injection complete.")
