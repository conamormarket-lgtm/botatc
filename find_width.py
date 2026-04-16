import ast

files_to_check = ['server.py', 'firebase_client.py', 'bot_atc.py', 'whatsapp_client.py']

for fname in files_to_check:
    try:
        with open(fname, encoding='utf-8') as f:
            src = f.read()
        # Buscar 'width' como nombre de variable en el AST
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == 'width':
                print(f'{fname}:{node.lineno}: Name(width) usado como variable')
            elif isinstance(node, ast.arg) and node.arg == 'width':
                print(f'{fname}:{node.lineno}: arg(width) - parametro de funcion')
    except SyntaxError as e:
        print(f'{fname}: SyntaxError - {e}')
    except FileNotFoundError:
        pass
