import re
with open("inbox.html", "r", encoding="utf-8") as f:
    s = f.read()

idx = s.find('{lista_chats_html}')
print(s[max(0, idx-400):idx+500])
