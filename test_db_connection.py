"""
Teste de conexão com PostgreSQL
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_postgresql_connection():
    """Testa conexão com PostgreSQL"""
    print("🔄 Testando conexão com PostgreSQL...")
    
    try:
        import psycopg2
        print("✅ psycopg2 disponível")
        
        # Obter URL de conexão
        db_url = os.environ.get('DEV_DATABASE_URL') or os.environ.get('DATABASE_URL')
        print(f"📍 URL do banco: {db_url}")
        
        if not db_url:
            print("❌ URL do banco não configurada")
            return False
        
        # Extrair parâmetros da URL
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        conn_params = {
            'host': parsed.hostname,
            'port': parsed.port,
            'database': parsed.path[1:],  # Remove o '/'
            'user': parsed.username,
            'password': parsed.password
        }
        
        print(f"🔌 Conectando em: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
        
        # Tentar conexão
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Teste simples
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Versão do PostgreSQL: {db_version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except ImportError:
        print("❌ psycopg2 não instalado")
        return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_sqlalchemy_connection():
    """Testa conexão com SQLAlchemy"""
    print("\n🔄 Testando conexão com SQLAlchemy...")
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.environ.get('DEV_DATABASE_URL') or os.environ.get('DATABASE_URL')
        
        # Configurar engine com encoding UTF-8 explícito
        engine = create_engine(
            db_url,
            client_encoding='utf8',
            echo=False
        )
        
        # Testar conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ SQLAlchemy conectou com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro SQLAlchemy: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("=" * 50)
    
    # Teste básico
    pg_ok = test_postgresql_connection()
    
    # Teste SQLAlchemy
    sql_ok = test_sqlalchemy_connection()
    
    print("\n" + "=" * 50)
    if pg_ok and sql_ok:
        print("🎉 Todos os testes passaram!")
        print("✅ Banco pronto para migrações")
    else:
        print("⚠️  Alguns testes falharam")
        print("📋 Verifique:")
        print("   • PostgreSQL está rodando?")
        print("   • Credenciais estão corretas?")
    print("   • Banco 'porvoce_dev' existe?")
    print("=" * 50)