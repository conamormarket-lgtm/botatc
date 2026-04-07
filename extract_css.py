import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'chat_view_css = """(.*?)"""', content, re.DOTALL)
if match:
    css = match.group(1)
    with open('extracted_css.txt', 'w', encoding='utf-8') as out:
        out.write(css)
    print("CSS extracted successfully")
else:
    print("Could not find chat_view_css")
