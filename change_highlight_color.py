string_color = '#009926'

with open('site/css/highlight.css', encoding='utf8') as f:
    data = f.read()
data = data.replace('#d14', string_color)
with open('site/css/highlight.css', 'w', encoding='utf8', newline='\n') as f:
    f.write(data)

with open('site/css/theme.css', encoding='utf8') as f:
    data = f.read()
before, after = data.split('.rst-content tt{white-space:nowrap;')
data = before + '.rst-content tt{white-space:nowrap;' + after.replace('#E74C3C', string_color, 1)
with open('site/css/theme.css', 'w', encoding='utf8', newline='\n') as f:
    f.write(data)
