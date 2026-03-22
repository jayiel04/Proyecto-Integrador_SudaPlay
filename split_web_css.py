import os
import re

css_filepath = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\apps\web\static\web\css\template_overrides.css'
out_dir = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\apps\web\static\web\css\pages'
templates_dir = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\apps\web\templates\web'
base_html = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\templates\base.html'

os.makedirs(out_dir, exist_ok=True)

with open(css_filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

slices = {
    'home-catalog.css': lines[0:484] + lines[1322:1444],
    'my-games.css': lines[484:625],
    'game-form.css': lines[625:696] + lines[1883:2298] + lines[2416:],
    'game-play.css': lines[696:816] + lines[816:1259] + lines[2298:2416],
    'audio-settings.css': lines[1259:1322] + lines[1705:1883],
    'web-info.css': lines[1444:1506],
    'review-games.css': lines[1506:1705]
}

for name, content in slices.items():
    path = os.path.join(out_dir, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(content)
    print(f"Created {name}")

# Backup and empty original
backup_path = css_filepath.replace('.css', '.backup.css')
os.replace(css_filepath, backup_path)
with open(css_filepath, 'w', encoding='utf-8') as f:
    f.write('/* File split into pages/ directory. Leaving this file empty to avoid 404s if cached */\n')
print("Backed up and emptied original template_overrides.css")

# --- HTML TEMPLATE UPDATES ---

mapping = {
    'home.html': 'home-catalog.css',
    'my_games.html': 'my-games.css',
    'game_form.html': 'game-form.css',
    'game_play.html': 'game-play.css',
    'advanced_audio_settings.html': 'audio-settings.css',
    'review_games.html': 'review-games.css',
    'about.html': 'web-info.css',
    'normas.html': 'web-info.css'
}

for tpl, css_file in mapping.items():
    tpl_path = os.path.join(templates_dir, tpl)
    if os.path.exists(tpl_path):
        with open(tpl_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        link_tag = f"""<link rel="stylesheet" href="{{% static 'web/css/pages/{css_file}' %}}?v=1">"""
        
        # Check if block extra_css exists
        if '{% block extra_css %}' in content:
            # Inject inside the block
            content = re.sub(r'({% block extra_css %})', r'\1\n    ' + link_tag, content, count=1)
        else:
            # Create the block after block title or extends
            # We'll put it after {% block content %} 's start if title doesn't exist, wait, standard is after extend
            # Let's insert after {% extends "base.html" %}
            block_code = f"\n{{% block extra_css %}}\n{link_tag}\n{{% endblock %}}\n"
            content = re.sub(r'({% extends ".*?" %})', r'\1' + block_code, content, count=1)
            
        with open(tpl_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {tpl}")

# Update base.html to remove the global overrides CSS
with open(base_html, 'r', encoding='utf-8') as f:
    base_content = f.read()

# removing:
#     {% if request.resolver_match.app_name == 'web' %}
#     <link rel="stylesheet" href="{% static 'web/css/template_overrides.css' %}?v=4">
#     {% endif %}
pattern = r"{%\s*if request\.resolver_match\.app_name == 'web'\s*%}\s*<link rel=\"stylesheet\" href=\"{% static 'web/css/template_overrides\.css' %}\?v=[0-9]+\">\s*{%\s*endif\s*%}"
base_content = re.sub(pattern, '', base_content)

with open(base_html, 'w', encoding='utf-8') as f:
    f.write(base_content)
print("Removed global web template_overrides.css from base.html")
