import sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('prompts.py', 'r', encoding='utf-8').read()
idx = s.find('def get_system_prompt')
print(s[idx:idx+800])
