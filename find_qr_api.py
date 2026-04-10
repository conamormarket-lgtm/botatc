import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
s = open('inbox.html', 'r', encoding='utf-8').read()

# Find the section where quick replies are listed/rendered and clicked
# Quick replies in the UI are usually shown in a panel and then clicked to insert text
idx = s.find('quick_replies')
if idx == -1:
    idx = s.find('quick-replies')
if idx == -1:
    idx = s.find('/api/quick')
    
print(f"idx={idx}")
if idx != -1:
    print(s[max(0,idx-100):idx+1000])
