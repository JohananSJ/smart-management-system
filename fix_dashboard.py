with open('templates/dashboard/dashboard.html', 'rb') as f:
    content = f.read()

content = content.replace(b'\xe2\x80\x94', b'&mdash;')
content = content.replace(b'\xe2\x86\x92', b'&rarr;')
content = content.replace(b'\xf0\x9f\x94\xa5', b'&#x1F525;')
content = content.replace(b'\xc3\xa2\xc2\x80\xc2\x94', b'&mdash;')
content = content.replace(b'\xc3\xa2\xc2\x86\xc2\x92', b'&rarr;')
content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xa5', b'&#x1F525;')

with open('templates/dashboard/dashboard.html', 'wb') as f:
    f.write(content)
print('Done')