"""Clean up server.py:
1. Remove the orphaned old renderQuickReplies duplicate code (lines 2173-2215)  
2. Fix the {{{msgs.length}}} which causes AttributeError (should be msgs.length in JS, escaped as {{msgs.length}} in f-string)
3. Remove the second copy of renderQuickReplies (lines 2244-2315)
"""

lines = open('server.py', 'r', encoding='utf-8').readlines()
print(f"Total lines: {len(lines)}")

# Fix line 2144 (1-indexed): {{{msgs.length}}} -> msgs.length in JS context
# In the f-string: `(${{{msgs.length}}} msgs)` is wrong, should be `(${{msgs.length}} msgs)`
for i, line in enumerate(lines):
    if 'msgs.length}}} msgs)' in line:
        old = line
        lines[i] = line.replace('${{{msgs.length}}} msgs)', '${{msgs.length}} msgs)')
        print(f"Fixed template literal at line {i+1}")
        break

# Find and remove the orphan block - lines 2173-2215 (0-indexed: 2172-2214)
# These lines start with "                    container.onmouseout = function() {{..."
# and end with "            }}"
# We look for the orphan by finding lines that seem to be in the middle of a forEach
# without proper function context

# Find the duplicate renderQuickReplies block at line 2244
# Find line index
start_dup = None
for i, line in enumerate(lines):
    if i > 2150 and 'function renderQuickReplies(data) {{' in line:
        start_dup = i
        print(f"Found duplicate renderQuickReplies at line {i+1}")
        break

# Also find the orphan block
orphan_start = None
orphan_end = None
for i, line in enumerate(lines):
    if i > 2170 and 'container.onmouseout = function()' in line and orphan_start is None:
        orphan_start = i
        print(f"Found orphan start at line {i+1}: {line.rstrip()}")
    if orphan_start and i > orphan_start and '            }}' == line.rstrip():
        orphan_end = i
        print(f"Found orphan end at line {i+1}")
        break

print(f"Orphan block: lines {orphan_start+1} to {orphan_end+1 if orphan_end else '?'}")

if orphan_start is not None and orphan_end is not None:
    # Remove orphan block + following duplicate renderQuickReplies
    # Find where the duplicate renderQuickReplies ends
    dup_end = None
    if start_dup:
        brace_depth = 0
        for i in range(start_dup, len(lines)):
            for ch in lines[i]:
                if ch == '{': brace_depth += 1
                elif ch == '}': brace_depth -= 1
            if brace_depth == 0 and i > start_dup:
                dup_end = i
                print(f"Duplicate renderQuickReplies ends at line {i+1}")
                break
    
    if start_dup and dup_end:
        # Remove orphan + filtrarQuickReplies + </script><script> + cargarQuickReplies + renderQuickReplies duplicate
        # Actually let's just remove all lines from orphan_start to dup_end inclusive
        del lines[orphan_start:dup_end+1]
        print(f"Removed lines {orphan_start+1} to {dup_end+1}")
    else:
        # Just remove orphan
        del lines[orphan_start:orphan_end+1]
        print(f"Removed orphan lines {orphan_start+1} to {orphan_end+1}")

open('server.py', 'w', encoding='utf-8').writelines(lines)
print(f"Saved. New line count: {len(lines)}")
