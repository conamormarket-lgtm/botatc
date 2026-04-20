import re
text='Ver https://google.com y www.bing.com'
def l(m):
  if m.group(1): return m.group(1)
  return m.group(2)
print(re.sub(r'(<[^>]+>)|(https?://[^\s<>]+|www\.[^\s<>]+)', l, text))
