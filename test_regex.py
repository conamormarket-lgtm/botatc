import re
def wrap_phone2(match):
    phone = match.group(1)
    clean_phone = __import__('re').sub(r'[\\s\\-]', '', phone)
    if sum(c.isdigit() for c in clean_phone) >= 7:
        return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \'{clean_phone}\')">{phone}</span>'
    return phone

print(re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{6,15}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone2, '997778512'))
