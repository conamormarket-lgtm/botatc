import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('server.py', 'r', encoding='utf-8').read()
idx = s.find('lista_chats_html +=')
print(s[max(0,idx-50):idx+800])
