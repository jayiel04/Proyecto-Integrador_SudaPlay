import sys

file_path = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\css\styles-navbar.css'

print("--- NAVBAR CSS STRUCTURE ---")
with open(file_path, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if line.startswith('/*') and line.endswith('*/'):
            print(f"Line {i}: {line}")
