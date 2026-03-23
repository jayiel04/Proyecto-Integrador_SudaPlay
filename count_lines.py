import os

total_lines = 0
total_files = 0
for d in ['static', 'apps']:
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.css'):
                total_files += 1
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                    total_lines += sum(1 for line in file)

print(f"Total CSS files: {total_files}")
print(f"Total CSS lines: {total_lines}")
