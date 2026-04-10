import re

with open("server.py", "r", encoding="utf-8") as f:
    text = f.read()

target = r""".bubble { max-width:80%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; }"""
rep = r""".bubble { max-width:85%; padding:0.8rem 1rem; border-radius:12px; font-size:0.95rem; line-height:1.4; position:relative; word-wrap:break-word; overflow-wrap:anywhere; box-sizing:border-box; }"""

if target in text:
    text = text.replace(target, rep)
    
target2_img = r"""style="width: 250px; max-width: 100%; max-height: 300px; border-radius: 8px; object-fit: cover; margin-bottom: 5px; cursor: zoom-in; box-sizing: border-box;"""
rep2_img = r"""style="width: 100%; max-width: 250px; max-height: 300px; border-radius: 8px; object-fit: cover; margin-bottom: 5px; cursor: zoom-in; box-sizing: border-box; display: block;"""

if target2_img in text:
    text = text.replace(target2_img, rep2_img)

target3_video = r"""style="width: 250px; max-width: 100%; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; box-sizing: border-box;"""
rep3_video = r"""style="width: 100%; max-width: 250px; max-height: 300px; border-radius: 8px; background: rgba(0,0,0,0.6); margin-bottom: 5px; box-sizing: border-box; display: block;"""

if target3_video in text:
    text = text.replace(target3_video, rep3_video)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed bubble wraps and image sizing")
