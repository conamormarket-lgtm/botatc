import os

def sanitize_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacing emojis with safe ascii
    content = content.replace("✅", "[OK]")
    content = content.replace("❌", "[ERROR]")
    content = content.replace("⚠️", "[WARN]")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

sanitize_file('server.py')
sanitize_file('firebase_client.py')
