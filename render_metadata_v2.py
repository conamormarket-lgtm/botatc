import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_burbujas = """            wamid_attr = f' data-wamid="{wamid}"' if wamid else ""
            burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr} title="Click derecho (PC) o mantener presionado (Móvil) para opciones">{texto_renderizado}</div>'
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")"""

new_burbujas = """            wamid_attr = f' data-wamid="{wamid}"' if wamid else ""

            import datetime
            meta_html = ""
            ts_html = ""
            status_html = ""

            if "timestamp" in m:
                try:
                    ts_val = int(m["timestamp"])
                    if ts_val > 1e11: ts_val //= 1000
                    ts_str = datetime.datetime.fromtimestamp(ts_val).strftime("%H:%M")
                    ts_html = f'<span class="msg-ts">{ts_str}</span>'
                except:
                    pass

            # Show tick only for assistant
            if es_bot and "status" in m:
                st = m["status"]
                if st == "sent":
                    tick = "✓"
                    color = "rgba(255,255,255,0.7)"
                elif st == "delivered":
                    tick = "✓✓"
                    color = "rgba(255,255,255,0.7)"
                elif st == "read":
                    tick = "✓✓"
                    color = "#34b7f1" 
                else:
                    tick = "✓"
                    color = "rgba(255,255,255,0.7)"
                status_html = f'<span class="msg-status" style="color:{color}; font-size:0.75rem; margin-left:4px; font-weight: bold;">{tick}</span>'

            if ts_html or status_html:
                meta_html = f'<div class="msg-meta" style="text-align:right; margin-top:4px; font-size:0.65rem; color:inherit; opacity:0.8; display:flex; justify-content:flex-end; align-items:center; gap:2px;">{ts_html}{status_html}</div>'

            burbujas += f'<div class="bubble {clase} {lado}"{wamid_attr} title="Click derecho (PC) o mantener presionado (Móvil) para opciones">{texto_renderizado}{meta_html}</div>'
            texto_renderizado = texto_renderizado.replace("</div> | ", "</div><br>")"""

if old_burbujas in text:
    text = text.replace(old_burbujas, new_burbujas)
    print("Replaced properly!")
else:
    print("Not found! old_burbujas doesn't match")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
