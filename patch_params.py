import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

old_href = 'lista_chats_html += f"""\n        <a href="/inbox/{num}?tab={tab}" class="chat-row {active_class}">'

new_href = '''extra_params = f"?tab={tab}"
        if label_filter: extra_params += f"&label={label_filter}"
        if unread: extra_params += f"&unread={unread}"
        
        lista_chats_html += f"""
        <a href="/inbox/{num}{extra_params}" class="chat-row {active_class}">'''

if 'extra_params =' not in text:
    text = text.replace(old_href, new_href)
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched params in server_py")
