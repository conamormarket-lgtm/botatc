import re

with open("inbox.html", "r", encoding="utf-8") as f:
    text = f.read()

target = r"""            const emojiMenu = document.getElementById("emojiMenu");
            if (emojiMenu && !e.target.closest('#emojiMenu') && !e.target.closest('button[title="Emojis"]')) {
                emojiMenu.style.display = "none";
            }"""

rep = r"""            const combinedEmojiMenu = document.getElementById("combinedEmojiMenu");
            if (combinedEmojiMenu && !e.target.closest('#combinedEmojiMenu') && !e.target.closest('button[title="Emojis y Stickers"]')) {
                combinedEmojiMenu.style.display = "none";
            }"""

if target in text:
    text = text.replace(target, rep)
    
    # Also replace any references to old emojiMenu and stickerMenu being hidden somewhere else
    # For instance 'emojiMenu.style.display = "none";'
    text = text.replace('const m = document.getElementById(\'emojiMenu\');\n                if (m) m.style.display = \'none\';', 'const m = document.getElementById(\'combinedEmojiMenu\');\n                if (m) m.style.display = \'none\';')
    
    with open("inbox.html", "w", encoding="utf-8") as f:
        f.write(text)
    print("Fixed document click off")
else:
    print("Target click off not found")
