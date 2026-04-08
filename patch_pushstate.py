import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

old_push = '''window.history.pushState(null, '', `/inbox?tab=${tab}`);'''
new_push = '''window.history.pushState(null, '', `/inbox${window.location.search}`);'''

if 'window.location.search' not in text.split('pushState')[1][:50]:
    text = text.replace(old_push, new_push)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Patched pushState in inbox.html")
