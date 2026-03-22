import os
import re

tpl_path = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\templates\web\review_games.html'

if os.path.exists(tpl_path):
    with open(tpl_path, 'r', encoding='utf-8') as f:
        content = f.read()

    link_tag = """<link rel="stylesheet" href="{% static 'web/css/pages/review-games.css' %}?v=1">"""
    
    if '{% block extra_css %}' in content:
        content = re.sub(r'({% block extra_css %})', r'\1\n{% load static %}\n    ' + link_tag, content, count=1)
    else:
        block_code = f"\n{{% block extra_css %}}\n{{% load static %}}\n{link_tag}\n{{% endblock %}}\n"
        content = re.sub(r'({%\s*extends\s+[^}]*%}\n?)', r'\1' + block_code, content, count=1)

    with open(tpl_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed review_games.html")
else:
    print("Not found")
