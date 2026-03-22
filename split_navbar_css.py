import os
import re

file_path = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\css\styles-navbar.css'
out_dir = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\css\components'
base_html = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\templates\base.html'

os.makedirs(out_dir, exist_ok=True)

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove comments for easier parsing, or we can keep them using a regex that matches blocks
# A better approach: use a regex that captures (1) normal rules, (2) media queries

# Regex to find top level rules and media queries.
# This assumes @media blocks are top level and have nested {}
# and normal selectors just have {}

def split_blocks(css_text):
    # This is a basic lexical scanner for CSS to handle nested braces safely
    blocks = []
    current_block = []
    brace_level = 0
    in_comment = False
    
    i = 0
    while i < len(css_text):
        char = css_text[i]
        
        # Handle comments
        if not in_comment and char == '/' and i + 1 < len(css_text) and css_text[i+1] == '*':
            in_comment = True
            current_block.append(char)
            current_block.append('*')
            i += 2
            continue
        elif in_comment and char == '*' and i + 1 < len(css_text) and css_text[i+1] == '/':
            in_comment = False
            current_block.append(char)
            current_block.append('/')
            i += 2
            continue

        if not in_comment:
            if char == '{':
                brace_level += 1
            elif char == '}':
                brace_level -= 1
                
        current_block.append(char)
        
        # If we hit 0 braces and char is '}', a block has ended!
        if not in_comment and brace_level == 0 and char == '}':
            blocks.append("".join(current_block))
            current_block = []
            
        i += 1
        
    if current_block:
        text = "".join(current_block).strip()
        if text:
            blocks.append(text)
            
    return blocks

blocks = split_blocks(content)

core_css = []
profile_css = []
chat_css = []
notif_css = []

def route_rule(rule_text):
    if '.profile-dropdown' in rule_text:
        return 'profile'
    elif '.profile-chat' in rule_text or '.chat-status' in rule_text or 'profile-chat-input' in rule_text:
        return 'chat'
    elif '.notification' in rule_text or 'upload-progress' in rule_text or 'navbar-badge' in rule_text:
        return 'notif'
    return 'core'

for block in blocks:
    if block.strip().startswith('@media') or block.strip().startswith('@keyframes'):
        # For @media, we must parse inner blocks and route them!
        # Find the first {
        first_brace = block.find('{')
        media_header = block[:first_brace+1]
        media_body = block[first_brace+1:-1] # everything except the last }
        
        inner_blocks = split_blocks(media_body)
        
        core_inner = []
        profile_inner = []
        chat_inner = []
        notif_inner = []
        
        for inner in inner_blocks:
            if not inner.strip():
                continue
            r = route_rule(inner)
            if r == 'profile':
                profile_inner.append(inner)
            elif r == 'chat':
                chat_inner.append(inner)
            elif r == 'notif':
                notif_inner.append(inner)
            else:
                core_inner.append(inner)
                
        if core_inner:
            core_css.append(media_header + "\n" + "\n".join(core_inner) + "\n}")
        if profile_inner:
            profile_css.append(media_header + "\n" + "\n".join(profile_inner) + "\n}")
        if chat_inner:
            chat_css.append(media_header + "\n" + "\n".join(chat_inner) + "\n}")
        if notif_inner:
            notif_css.append(media_header + "\n" + "\n".join(notif_inner) + "\n}")
    else:
        # Normal rule
        r = route_rule(block)
        if r == 'profile':
            profile_css.append(block)
        elif r == 'chat':
            chat_css.append(block)
        elif r == 'notif':
            notif_css.append(block)
        else:
            core_css.append(block)

# Backup original
backup_path = file_path.replace('.css', '.backup.css')
os.replace(file_path, backup_path)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write("\n\n".join(core_css))
    
with open(os.path.join(out_dir, 'navbar-profile.css'), 'w', encoding='utf-8') as f:
    f.write("\n\n".join(profile_css))

with open(os.path.join(out_dir, 'navbar-chat.css'), 'w', encoding='utf-8') as f:
    f.write("\n\n".join(chat_css))

with open(os.path.join(out_dir, 'navbar-notifications.css'), 'w', encoding='utf-8') as f:
    f.write("\n\n".join(notif_css))

print('Split complete. Updating base.html...')

with open(base_html, 'r', encoding='utf-8') as f:
    base_content = f.read()

injection = """    <link rel="stylesheet" href="{% static 'css/components/navbar-profile.css' %}?v=1">
    <link rel="stylesheet" href="{% static 'css/components/navbar-chat.css' %}?v=1">
    <link rel="stylesheet" href="{% static 'css/components/navbar-notifications.css' %}?v=1">
"""

if "navbar-profile.css" not in base_content:
    base_content = base_content.replace(
        """    <link rel="stylesheet" href="{% static 'css/components/profile.css' %}?v=1">""",
        injection + """    <link rel="stylesheet" href="{% static 'css/components/profile.css' %}?v=1">"""
    )
    with open(base_html, 'w', encoding='utf-8') as f:
        f.write(base_content)
    print('Updated base.html.')
else:
    print('Links already in base.html')

print('Done.')
