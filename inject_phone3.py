import re

with open("server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    # Search for both instances
    if "texto  = m[\"content\"].replace(\"\\\\n\", \"<br>\")" in line or "texto     = m[\"content\"].replace(\"\\n\", \"<br>\")" in line:
        # Avoid duplicate replacement if we run this multiple times
        # get indentation string
        indent = line[:len(line) - len(line.lstrip())]
        block = f"""
{indent}def wrap_phone(match):
{indent}    phone = match.group(1)
{indent}    clean_phone = __import__('re').sub(r'[\\s\\-]', '', phone)
{indent}    if sum(c.isdigit() for c in clean_phone) >= 7:
{indent}        return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \\'{{clean_phone}}\\')">{{phone}}</span>'
{indent}    return phone
{indent}texto = __import__('re').sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{{6,15}}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)
"""
        new_lines.append(block)

# Join the lines, then check for duplicates and remove them
final_text = "".join(new_lines)
# Clean up duplicate wrap_phone blocks if any
import re
final_text = re.sub(r'(def wrap_phone\(match\):.*?texto = __import__\(\'re\'\)\.sub.*?)\s+def wrap_phone', r'\1', final_text, flags=re.DOTALL)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(final_text)

print("Injected via direct line match")
