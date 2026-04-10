import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('prompts.py', 'r', encoding='utf-8').read()
print(s[:1000])
