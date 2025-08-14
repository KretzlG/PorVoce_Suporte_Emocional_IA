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
        assert db_url, "URL do banco não configurada"
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
        assert db_version is not None, "Não foi possível obter versão do PostgreSQL"
    except ImportError:
        print("❌ psycopg2 não instalado")
        assert False, "psycopg2 não instalado"
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        assert False, f"Erro de conexão: {e}"

def test_sqlalchemy_connection():
    """Testa conexão com SQLAlchemy"""
    print("\n🔄 Testando conexão com SQLAlchemy...")
    
    try:
        from sqlalchemy import create_engine, text
        db_url = os.environ.get('DEV_DATABASE_URL') or os.environ.get('DATABASE_URL')
        engine = create_engine(
            db_url,
            client_encoding='utf8',
            echo=False
        )
        # Testar conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ SQLAlchemy conectou com sucesso!")
            assert result.fetchone()[0] == 1, "SQLAlchemy não retornou 1"
    except Exception as e:
        print(f"❌ Erro SQLAlchemy: {e}")
        assert False, f"Erro SQLAlchemy: {e}"

