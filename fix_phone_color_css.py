import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = "<style>"
rep = """<style>
        .bubble-user .chat-phone { color: var(--primary-color) !important; text-decoration: underline; font-weight: bold; }
        .bubble-bot .chat-phone { color: #ffffff !important; text-decoration: underline; font-weight: bold; }"""

if target in text:
    text = text.replace(target, rep)
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Injected CSS")
