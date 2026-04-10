import sys
import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

def escape_braces(match):
    s = match.group(0)
    s = s.replace("{", "{{").replace("}", "}}")
    return s

# Match the JS block <script> ... </script> after <script src="https://accounts.google.com/gsi/client"
text = re.sub(r'<script>\s*function setMode\(mode\).*?google_token.*?</script>', escape_braces, text, flags=re.DOTALL)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed braces")
