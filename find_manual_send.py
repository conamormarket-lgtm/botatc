import sys
import re

ss = open('server.py', 'r', encoding='utf-8').read()

# 1. Add sent_by to each message: we need to store sent_by in the message dict when saving
# First let's see how manual messages are stored (sent_by the human agent)
idx = ss.find('enviar_manual')
print(ss[max(0,idx-100):idx+600])
