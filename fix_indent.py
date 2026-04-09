import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

# Remove the broken block
broken_block = re.search(r'(\s+)texto\s*=\s*m\[\"content\"\]\.replace\(\"\\n\"\,\s*\"<br>\"\)\s+def wrap_phone.*?texto = re\.sub[^\n]+', text, flags=re.DOTALL)
if broken_block:
    # restore it to its original line
    orig_indent = broken_block.group(1).split("\n")[-1]
    orig_line = orig_indent + 'texto     = m["content"].replace("\\n", "<br>")'
    text = text.replace(broken_block.group(0), orig_line)
    print("Fixed broken block")

# Let's cleanly inject wrap_phone replacing ALL instances of texto = m["content"].replace("\\n", "<br>")
def replacer(match):
    indent = match.group(1).lstrip('\r\n')
    line = match.group(0)
    return line + f"""
{indent}def wrap_phone(match):
{indent}    phone = match.group(1)
{indent}    clean_phone = re.sub(r'[\\s\\-]', '', phone)
{indent}    if sum(c.isdigit() for c in clean_phone) >= 7:
{indent}        return f'<span class="chat-phone" style="color:var(--primary-color); text-decoration:underline; cursor:pointer; font-weight:500;" onclick="abrirCtxTelefono(event, \\\\'{{clean_phone}}\\\\')">{{phone}}</span>'
{indent}    return phone
{indent}texto = re.sub(r'(?<![a-zA-Z0-9\:\-\/\.\=\_])(\+?\d[\d\s\-]{{6,15}}\d)(?![a-zA-Z0-9\.\-\/\=\_])', wrap_phone, texto)"""

new_text = re.sub(r'(\n[ \t]+)texto\s*=\s*m\[\"content\"\]\.replace\(\"\\n\",\s*\"<br>\"\)', replacer, text)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(new_text)
print("Applied dynamic indentation fix!")
