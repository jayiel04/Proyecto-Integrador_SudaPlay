import os
from pathlib import Path

project_root = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay'
ignore_dirs = ['.venv', 'venv', '.git', 'node_modules', '__pycache__']

css_files = []

for root, dirs, files in os.walk(project_root):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        if file.endswith('.css'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    css_files.append((path, len(lines)))
            except Exception as e:
                pass

css_files.sort(key=lambda x: x[1], reverse=True)

print("--- CSS FILES SORTED BY LINE COUNT ---")
for path, lines in css_files:
    if lines > 0:
        rel_path = os.path.relpath(path, project_root)
        print(f"{lines:5d} lines - {rel_path}")
