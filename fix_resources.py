import re
with open('templates/resources/resources.html', 'r', encoding='utf-8') as f:
    content = f.read()
print('Before:', 'f.filename' in content)
content = re.sub(r'f\.filename', 'f.file_name', content)
content = re.sub(r'f\.original_filename \|\| f\.file_name', 'f.file_name', content)
with open('templates/resources/resources.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print('After:', 'f.filename' in content)
