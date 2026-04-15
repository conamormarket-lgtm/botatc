import codecs

try:
    with open('inbox.html', 'rb') as f:
        content = f.read()

    # Intenta decodificar con utf-8, si falla con latin-1, si algo falla lo arregla
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        text = content.decode('latin-1')

    # Convertir entidades corruptas t?picas
    text = text.replace('\u00f3', 'ó')
    text = text.replace('\u00fa', 'ú')
    text = text.replace('\u00e1', 'á')
    text = text.replace('\u00e9', 'é')
    text = text.replace('\u00ed', 'í')

    with open('inbox.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed!")
except Exception as e:
    print("Error:", e)
