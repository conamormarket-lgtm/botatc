import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find message rendering - look for the JS function that creates bubbles
idx = s.find('bubble-bot')
print(s[max(0,idx-300):idx+600])
