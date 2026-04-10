import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target_img = """elif tipo == "imagen":
                    return f\"\"\"<div style="text-align:center;"><img src="{src_url}" style="max-width: 100%; max-height: 400px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>\"\"\""""

target_vid = """elif tipo == "video":
                    return f\"\"\"<div style="text-align:center;"><video controls src="{src_url}" style="width: 100%; max-width: 250px; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; box-sizing: border-box; display: block;"></video></div>\"\"\""""

rep_img = """elif tipo == "imagen":
                    return f\"\"\"<div style="text-align:center; max-width: 350px; margin: 0 auto;"><img src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.2); margin-bottom: 5px; display: block; margin: 0 auto; cursor: zoom-in;" alt="Imagen {media_id}" onerror="this.onerror=null; this.src='https://placehold.co/250x150?text=Imagen';"></div>\"\"\""""

rep_vid = """elif tipo == "video":
                    return f\"\"\"<div style="text-align:center; max-width: 350px; margin: 0 auto;"><video controls src="{src_url}" style="max-width: 100%; max-height: 350px; width: auto; object-fit: contain; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; display: block; margin: 0 auto;"></video></div>\"\"\""""


if target_img in text:
    text = text.replace(target_img, rep_img)
    print("Replaced IMG container")
if target_vid in text:
    text = text.replace(target_vid, rep_vid)
    print("Replaced VID container")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
