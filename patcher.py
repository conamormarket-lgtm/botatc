import re
import os

code = open('server.py', 'r', encoding='utf-8').read()

# Extract the script
script_match = re.search(r'(\s*<script>\n\s*let quickRepliesCache = \[\];.*?</script>\n)', code, re.DOTALL)
if script_match:
    script = script_match.group(1)
    # Remove it from its original location
    code = code.replace(script, '')
    
    # Append it right before the chatScroll script block at the bottom
    target = "<script>\n            var c = document.getElementById('chatScroll');"
    code = code.replace(target, script + "            " + target)
    
    open('server.py', 'w', encoding='utf-8').write(code)
    print("Patched successfully!")
else:
    print("Script block not found!")
