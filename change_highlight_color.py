code_color = '#009926'

with open('site/css/theme_extra.css', encoding='utf8') as f:
    data = f.read()
before, after = data.rsplit('.rst-content code {', maxsplit=1)
data = before + '.rst-content code {' + after.replace('#E74C3C', code_color, 1)
with open('site/css/theme_extra.css', 'w', encoding='utf8', newline='\n') as f:
    f.write(data)
