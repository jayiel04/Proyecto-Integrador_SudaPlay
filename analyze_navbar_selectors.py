import sys
import re

file_path = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\css\styles-navbar.css'

prefixes = {
    'profile-dropdown': 0,
    'profile-chat': 0,
    'notification': 0,
    'navbar-brand': 0,
    'navbar-menu': 0,
    'nav-link': 0,
    'navbar': 0, # core
    'upload': 0,
}

current_rule_lines = 0
in_rule = False
current_prefixes = set()

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        # Simplistic parsing
        line = line.strip()
        if '{' in line:
            in_rule = True
            # guess prefixes
            for p in prefixes:
                if p in line:
                    current_prefixes.add(p)
        if in_rule:
            current_rule_lines += 1
        else:
            for p in prefixes:
                if p in line:
                    current_prefixes.add(p)
        
        if '}' in line:
            in_rule = False
            for p in current_prefixes:
                prefixes[p] += current_rule_lines
            current_rule_lines = 0
            current_prefixes = set()

print("Approximate line counts by component prefix:")
for p, count in prefixes.items():
    print(f"  {p}: {count} lines")
