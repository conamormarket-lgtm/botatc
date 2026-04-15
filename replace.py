import sys, re
with open('whatsapp_client.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    'def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None) -> bool:\n',
    'def enviar_media(numero_destino: str, tipo_media: str, media_id_o_url: str, reply_to_wamid: str = None, caption: str = None) -> bool:\n'
)
c = c.replace(
    'if tipo_media == "audio":\n        media_obj["voice"] = True\n',
    'if tipo_media == "audio":\n        media_obj["voice"] = True\n    if caption and tipo_media in ["image", "video", "document"]:\n        media_obj["caption"] = caption\n'
)
with open('whatsapp_client.py', 'w', encoding='utf-8') as f:
    f.write(c)

with open('server.py', 'r', encoding='utf-8') as f:
    s = f.read()

split_old = "partes = re.split(r'(\\[sticker:[^\\]]+\\]|\\[imagen:[^\\]]+\\]|\\[video:[^\\]]+\\]|\\[audio:[^\\]]+\\]|\\[sticker-local:[^\\]]+\\]|\\[documento:[^\\]]+\\])', texto)"
split_new = "partes = re.split(r'(\\[(?:sticker|imagen|video|audio|sticker-local|documento):[^\\]]+\\])', texto)"
s = s.replace(split_old, split_new)

r_old = '''match_sticker = re.match(r"^\[sticker:([^\]]+)\]$", p)
                match_img = re.match(r"^\[imagen:([^\]]+)\]$", p)
                match_video = re.match(r"^\[video:([^\]]+)\]$", p)
                match_audio = re.match(r"^\[audio:([^\]]+)\]$", p)
                match_doc = re.match(r"^\[documento:([^\]]+)\]$", p)
                match_sticker_local = re.match(r"^\[sticker-local:([^\]]+)\]$", p)
                
                w_id_current = None
                try:
                    if match_sticker: 
                        w_id_current = enviar_media(target, "sticker", match_sticker.group(1))
                    elif match_img: 
                        w_id_current = enviar_media(target, "image", match_img.group(1))
                    elif match_video:
                        w_id_current = enviar_media(target, "video", match_video.group(1))
                    elif match_doc:
                        w_id_current = enviar_media(target, "document", match_doc.group(1))
                    elif match_audio:'''

r_new = '''match_sticker = re.match(r"^\[sticker:([^\|\]]+)\]$", p)
                match_img = re.match(r"^\[imagen:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_video = re.match(r"^\[video:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_audio = re.match(r"^\[audio:([^\|\]]+)\]$", p)
                match_doc = re.match(r"^\[documento:([^\|\]]+)(?:\|caption:(.*?))?\]$", p)
                match_sticker_local = re.match(r"^\[sticker-local:([^\|\]]+)\]$", p)
                
                w_id_current = None
                try:
                    import urllib.parse
                    if match_sticker: 
                        w_id_current = enviar_media(target, "sticker", match_sticker.group(1))
                    elif match_img:
                        cap = urllib.parse.unquote(match_img.group(2)) if match_img.group(2) else None
                        w_id_current = enviar_media(target, "image", match_img.group(1), caption=cap)
                    elif match_video:
                        cap = urllib.parse.unquote(match_video.group(2)) if match_video.group(2) else None
                        w_id_current = enviar_media(target, "video", match_video.group(1), caption=cap)
                    elif match_doc:
                        cap = urllib.parse.unquote(match_doc.group(2)) if match_doc.group(2) else None
                        w_id_current = enviar_media(target, "document", match_doc.group(1), caption=cap)
                    elif match_audio:'''

s = s.replace(r_old, r_new)
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(s)
