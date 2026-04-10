import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('inbox.html', 'r', encoding='utf-8').read()
idx = s.find('class="chats-container"')
print(s[max(0,idx-150):idx+250])
