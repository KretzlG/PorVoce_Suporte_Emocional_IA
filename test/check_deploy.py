#!/usr/bin/env python3
"""
Script para verificar se a aplicação está pronta para deploy no Render
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (FALTANDO)")
        return False

def check_requirements():
    """Verifica se gunicorn está no requirements.txt"""
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                with open('requirements.txt', 'r', encoding=encoding) as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("❌ Não foi possível ler requirements.txt")
            return False
            
        if 'gunicorn' in content:
            print("✅ Gunicorn encontrado no requirements.txt")
            return True
        else:
            print("❌ Gunicorn NÃO encontrado no requirements.txt")
            return False
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado")
        return False

def check_app_import():
    """Verifica se a aplicação pode ser importada corretamente"""
    print("\n🔍 Verificando importação da aplicação:")
    
    try:
        # Teste 1: Importar o módulo wsgi
        print("  1. Importando módulo wsgi...")
        import wsgi as wsgi_module
        print("     ✅ Módulo wsgi importado com sucesso")
        
        # Teste 2: Importar a aplicação Flask
        print("  2. Importando aplicação Flask...")
        from wsgi import app
        print(f"     ✅ Aplicação importada: {type(app)}")
        
        # Teste 3: Verificar se app é uma instância Flask válida
        print("  3. Verificando tipo da aplicação...")
        from flask import Flask
        if isinstance(app, Flask):
            print("     ✅ app é uma instância Flask válida")
        else:
            print(f"     ❌ app não é uma instância Flask: {type(app)}")
            return False
        
        # Teste 4: Simular importação do gunicorn
        print("  4. Simulando importação do gunicorn...")
        import importlib
        module = importlib.import_module('wsgi')
        gunicorn_app = getattr(module, 'app')
        print(f"     ✅ Gunicorn pode acessar wsgi:app: {type(gunicorn_app)}")
        
        return True
        
    except ImportError as e:
        print(f"     ❌ Erro de importação: {e}")
        return False
    except AttributeError as e:
        print(f"     ❌ Erro de atributo: {e}")
        print("     💡 Certifique-se que existe 'app' no arquivo wsgi.py")
        return False
    except Exception as e:
        print(f"     ❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_env_vars():
    """Verifica variáveis de ambiente essenciais"""
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    optional_vars = [
        'OPENAI_API_KEY',
        'JWT_SECRET_KEY'
    ]
    
    print("\n🔍 Verificando variáveis de ambiente necessárias:")
    
    missing_required = []
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var}: configurado")
        else:
            print(f"⚠️  {var}: NÃO configurado (será necessário no Render)")
            missing_required.append(var)
    
    for var in optional_vars:
        if os.environ.get(var):
            print(f"✅ {var}: configurado")
        else:
            print(f"ℹ️  {var}: não configurado (opcional)")
    
    return len(missing_required) == 0
    
    return len(missing_required) == 0

def main():
    """Função principal de verificação"""
    print("🚀 VERIFICAÇÃO PRÉ-DEPLOY PARA RENDER")
    print("=" * 50)
    
    all_good = True
    
    # Verificar arquivos essenciais
    print("\n📁 Verificando arquivos essenciais:")
    files_to_check = [
        ('requirements.txt', 'Dependências Python'),
        ('wsgi.py', 'Arquivo principal WSGI'),
        ('config.py', 'Configurações'),
        ('Procfile', 'Comando de execução'),
        ('runtime.txt', 'Versão do Python'),
        ('render.yaml', 'Configuração do Render'),
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Verificar requirements.txt
    print("\n📦 Verificando dependências:")
    if not check_requirements():
        all_good = False
    
    # Verificar estrutura da aplicação
    print("\n🏗️  Verificando estrutura da aplicação:")
    app_structure = [
        ('app/__init__.py', 'Inicialização da app'),
        ('app/routes/', 'Rotas'),
        ('app/models/', 'Modelos'),
        ('migrations/', 'Migrações do banco'),
    ]
    
    for path, description in app_structure:
        if not check_file_exists(path, description):
            all_good = False
    
    # Verificar importação da aplicação
    if not check_app_import():
        all_good = False
    
    # Verificar variáveis de ambiente
    if not check_env_vars():
        all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 TUDO PRONTO PARA DEPLOY!")
        print("\n📋 Próximos passos:")
        print("1. Faça commit e push das alterações")
        print("2. Crie conta no Render (render.com)")
        print("3. Crie PostgreSQL database")
        print("4. Crie Web Service conectado ao seu repo")
        print("5. Configure as variáveis de ambiente")
        print("6. Aguarde o deploy completar")
        return 0
    else:
        print("⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        print("Corrija os itens marcados com ❌ antes do deploy")
        return 1

if __name__ == '__main__':
    sys.exit(main())
