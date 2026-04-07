"""Fix the broken regex line"""
code = open('server.py', 'r', encoding='utf-8').read()

# The broken regex line - find it and replace it
old = "                    const slashMatch = input.value.match(/(?:^|\\\\\\\\s)\\\\\\\\/$/); \r\n                    if (slashMatch) {{"
new = "                    const endsWithSlash = input.value.trimEnd().endsWith(\"/\");\r\n                    if (endsWithSlash) {{"

if old in code:
    code = code.replace(old, new)
    print("Fixed regex line!")
else:
    # Try without \r
    old2 = old.replace('\r\n', '\n')
    new2 = new.replace('\r\n', '\n')
    if old2 in code:
        code = code.replace(old2, new2)
        print("Fixed regex line (LF)!")
    else:
        # Find the line another way
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'slashMatch' in line and 'regex' not in line:
                print(f"Found at line {i+1}: {repr(line)}")
                lines[i] = '                    const endsWithSlash = input.value.trimEnd().endsWith("/");'
                # Fix next line too
                if 'slashMatch' in lines[i+1]:
                    lines[i+1] = lines[i+1].replace('slashMatch', 'endsWithSlash')
                code = '\n'.join(lines)
                print("Fixed by line scan!")
                break
        else:
            print("ERROR: Could not find slashMatch line")
            exit(1)

open('server.py', 'w', encoding='utf-8').write(code)
print("Saved.")
