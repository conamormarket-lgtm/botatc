import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_logic = '''        for m in msgs:
            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-izq" if es_bot else "lado-der"
            texto  = m["content"].replace("\\n", "<br>")'''

new_logic = '''        for m in msgs:
            es_bot = m["role"] == "assistant"
            clase  = "bubble-bot" if es_bot else "bubble-user"
            lado   = "lado-der" if es_bot else "lado-izq"
            texto  = m["content"].replace("\\n", "<br>")'''
text = text.replace(old_logic, new_logic)

old_visor = '''      .bot-lado{align-self:flex-start}
      .user-lado{align-self:flex-end}
      .remitente{font-size:.75rem;color:var(--text-gray);margin-bottom:.25rem;font-weight:600}
      .user-lado .remitente{text-align:right}
      .burbuja-bot{background:var(--wa-bot);border-radius:0 12px 12px 12px;padding:.75rem 1rem;
                   font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                   color:var(--text-dark);position:relative}
      .burbuja-user{background:white;border-radius:12px 0 12px 12px;padding:.75rem 1rem;
                   font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                   color:var(--text-dark);position:relative}'''

new_visor = '''      .bot-lado{align-self:flex-end}
      .user-lado{align-self:flex-start}
      .remitente{font-size:.75rem;color:var(--text-gray);margin-bottom:.25rem;font-weight:600}
      .bot-lado .remitente{text-align:right}
      .burbuja-bot{background:var(--wa-bot);border-radius:12px 0 12px 12px;padding:.75rem 1rem;
                   font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                   color:var(--text-dark);position:relative}
      .burbuja-user{background:white;border-radius:0 12px 12px 12px;padding:.75rem 1rem;
                   font-size:.95rem;line-height:1.45;box-shadow:0 1px 2px rgba(0,0,0,.1);
                   color:var(--text-dark);position:relative}'''
text = text.replace(old_visor, new_visor)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated server.py buble sides")
