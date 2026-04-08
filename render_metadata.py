import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_burbujas = """            else:
                pass # Already structured

            burbujas += f'<div class="bubble {clase} {lado}">{texto}</div>'"""

new_burbujas = """            else:
                pass # Already structured

            import datetime
            meta_html = ""
            ts_html = ""
            status_html = ""
            
            if "timestamp" in m:
                try:
                    ts_val = int(m["timestamp"])
                    # Fallback if extremely large
                    if ts_val > 1e11: ts_val //= 1000
                    ts_str = datetime.datetime.fromtimestamp(ts_val).strftime("%H:%M")
                    ts_html = f'<span class="msg-ts">{ts_str}</span>'
                except:
                    pass
            
            # Show tick only for assistant (sent, delivered, read)
            if es_bot and "status" in m:
                st = m["status"]
                if st == "sent":
                    tick = "✓"
                    color = "#ffffff"
                elif st == "delivered":
                    tick = "✓✓"
                    color = "#ffffff"
                elif st == "read":
                    tick = "✓✓"
                    color = "#00ffff" # cyan/blueish for read receipts on dark blue bg
                else:
                    tick = "✓"
                    color = "#ffffff"
                status_html = f'<span class="msg-status" style="color:{color}; font-size:0.8rem; margin-left:4px;">{tick}</span>'

            if ts_html or status_html:
                meta_html = f'<div class="msg-meta" style="text-align:right; margin-top:4px; font-size:0.7rem; color:inherit; opacity:0.8; display:flex; justify-content:flex-end; align-items:center; gap:4px;">{ts_html} {status_html}</div>'

            burbujas += f'<div class="bubble {clase} {lado}">{texto}{meta_html}</div>'"""

text = text.replace(old_burbujas, new_burbujas)

# ALSO update ver_chat rendering exactly the same way to keep it consistent
old_burbujas2 = """          <div class="{lado}">
            <div class="{clase}">
              {texto}
            </div>
          </div>"""

new_burbujas2 = """          <div class="{lado}">
            <div class="{clase}">
              {texto}
            </div>
          </div>""" # no change yet, wait, we don't need to change ver_chat if the user is testing inbox! Let's just focus on inbox_chat!

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated bubbles to include timestamp and status")
