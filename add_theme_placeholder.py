# Agrega el placeholder {custom_theme_css} antes de </head> en admin.html y usuarios.html

for filename in ['admin.html', 'usuarios.html']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '{custom_theme_css}' in content:
        print(f'{filename}: YA tiene placeholder, saltando')
        continue
    
    # Buscar el patron exacto del cierre de style + head
    old = '    </style>\n</head>'
    new = '    </style>\n    <style id="custom-theme-css">\n{custom_theme_css}\n    </style>\n</head>'
    
    if old in content:
        content = content.replace(old, new, 1)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{filename}: OK - placeholder agregado')
    else:
        # Intentar con CRLF
        old2 = '    </style>\r\n</head>'
        new2 = '    </style>\r\n    <style id="custom-theme-css">\r\n{custom_theme_css}\r\n    </style>\r\n</head>'
        if old2 in content:
            content = content.replace(old2, new2, 1)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'{filename}: OK (CRLF) - placeholder agregado')
        else:
            # Buscar el ultimo </style>\n</head> o variante
            import re
            idx = content.rfind('</style>')
            idx2 = content.find('</head>', idx)
            if idx >= 0 and idx2 >= 0:
                before = content[:idx2]
                after = content[idx2:]
                content = before + '\n    <style id="custom-theme-css">\n{custom_theme_css}\n    </style>\n' + after
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'{filename}: OK (fallback regex) - placeholder agregado')
            else:
                print(f'{filename}: ERROR - no se encontro patron')
    
    # Verificar
    with open(filename, 'r', encoding='utf-8') as f:
        check = f.read()
    print(f'  Verificacion: {"OK" if "{custom_theme_css}" in check else "FALLO"}')
