import os
import chardet

# Caminhos para checar (adicione outros se quiser)
dirs_to_check = [
    'migrations',
    'app/models'
]

for dir_path in dirs_to_check:
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    raw = f.read()
                    result = chardet.detect(raw)
                    encoding = result['encoding']
                    print(f'{file_path}: {encoding}')
                    if encoding.lower() != 'utf-8':
                        print(f'  >>> ATENÇÃO: {file_path} NÃO está em UTF-8!')
