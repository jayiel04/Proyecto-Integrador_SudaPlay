import os

my_games_css = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\apps\web\static\web\css\pages\my-games.css'
pages_css = r'c:\Users\javie\OneDrive\Desktop\Proyecto-Integrador_SudaPlay\static\css\pages.css'

with open(my_games_css, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The class is defined roughly around line 69-96 depending on lines list
extract_start = -1
extract_end = -1

for i, line in enumerate(lines):
    if '.login-card.full-width-card' in line:
        extract_start = i
        break

if extract_start != -1:
    for i in range(extract_start, len(lines)):
        # Look for the end of the full-width-card::-webkit-scrollbar-thumb block
        if '.full-width-card::-webkit-scrollbar-thumb {' in lines[i]:
            # find closing brace for this block
            for j in range(i, len(lines)):
                if '}' in lines[j]:
                    extract_end = j
                    break
            break

if extract_start != -1 and extract_end != -1:
    extracted_content = lines[extract_start:extract_end+1]
    
    # Remove from my-games.css
    new_my_games = lines[:extract_start] + lines[extract_end+1:]
    with open(my_games_css, 'w', encoding='utf-8') as f:
        f.writelines(new_my_games)
    
    # Append to pages.css
    with open(pages_css, 'a', encoding='utf-8') as f:
        f.write('\n/* Global Full Width Card overrides */\n')
        f.writelines(extracted_content)
        f.write('\n')

    print("Successfully moved .full-width-card classes to pages.css")
else:
    print("Could not find blocks in my-games.css:", extract_start, extract_end)
