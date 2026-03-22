import os
import re

templates = [
    'home.html',
    'my_games.html',
    'game_form.html',
    'game_play.html',
    'advanced_audio_settings.html',
    'review_games.html',
    'about.html',
    'normas.html'
]
templates_dir = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\apps\web\templates\web'

for tpl in templates:
    tpl_path = os.path.join(templates_dir, tpl)
    if os.path.exists(tpl_path):
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove all existing load static tags
        content = re.sub(r'{%\s*load static\s*%}\n?', '', content)
        
        # Insert load static immediately after extends
        content = re.sub(r'({%\s*extends\s+[^}]*%}\n?)', r'\1{% load static %}\n', content, count=1)
        
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {tpl}")
