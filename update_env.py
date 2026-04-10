import re

with open(".env", "r", encoding="utf-8") as f:
    text = f.read()

text = re.sub(r'META_ACCESS_TOKEN=.*', 'META_ACCESS_TOKEN=EAAVZAMGZCnNBIBRC1FVqLvCYGZCePVz3dDuJ24gm1c7z76sNuGJfswKeBkZB42iOxH2uCxc4E5gjYpTjEE5mNZAi7fXQBPYZBk4n8CIZAl2waV5KuOah4PGM4BE3SEVnjulbOTtMNlAaQZB2w5XXcK1wzbjbKDKp583bQoBm98eyLZA9zZAfVebXvgBuLA18eJigZDZD', text)

with open(".env", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated .env")
