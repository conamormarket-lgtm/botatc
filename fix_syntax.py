import sys
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    """\n.replace("__ERR_HTML__", err_html)', '    """')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed syntax error")
