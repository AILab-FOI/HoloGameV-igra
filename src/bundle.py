#!/usr/bin/env python3
import os

moduli_dir = 'modules'
main_file_path = os.path.join(moduli_dir, 'M_main.py')
knights_quest_file_path = 'knights_quest.py'

with open(main_file_path, 'r') as main_file:
    main_content = main_file.read()

with open(knights_quest_file_path, 'r') as knights_quest_file:
    knights_quest_content = knights_quest_file.read()

main_content_parts = main_content.split('# <TILES>')

knights_quest_content_parts = knights_quest_content.split('# <TILES>')

new_file_content = main_content_parts[0]

for filename in os.listdir(moduli_dir):
    file_path = os.path.join(moduli_dir, filename)
    # Skip the M_main.py file
    if filename == 'M_main.py' or not filename.endswith('.py'):
        continue
    with open(file_path, 'r') as file:
        new_file_content += '\n' + file.read()

new_file_content += '\n# <TILES>' + '<TILES>'.join(knights_quest_content_parts[1:])

with open('knights_quest.py', 'w') as new_file:
    new_file.write(new_file_content)

print("Bundling completed.")

