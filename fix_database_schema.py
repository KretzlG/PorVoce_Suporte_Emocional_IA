#!/usr/bin/env python3
"""
Script para corrigir o schema do banco de dados
Adiciona a coluna 'score' na tabela training_data e corrige problemas de schema
"""

import os
import sys
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError

# Configurar variáveis de ambiente se não estiverem definidas
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://localhost/porvoce_db'

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app, db
    from config import Config
except ImportError as e:
    print(f"Erro ao importar módulos da aplicação: {e}")
    print("Tentando criar conexão direta com o banco...")
    
    # Fallback: conexão direta
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/porvoce_db')
    engine = create_engine(DATABASE_URL)


def check_column_exists(connection, table_name, column_name):
    """Verifica se uma coluna existe na tabela"""
    try:
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name 
            AND column_name = :column_name
        """), {'table_name': table_name, 'column_name': column_name})
        
        return result.fetchone() is not None
    except Exception as e:
        print(f"Erro ao verificar coluna {column_name}: {e}")
        return False


def add_score_column():
    """Adiciona a coluna score na tabela training_data"""
    
    print("🔧 CORRIGINDO SCHEMA DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Usar a aplicação Flask se disponível
        if 'create_app' in globals():
            app = create_app()
            with app.app_context():
                connection = db.engine.connect()
                trans = connection.begin()
        else:
            # Conexão direta
            connection = engine.connect()
            trans = connection.begin()
        
        try:
            # 1. Verificar se a coluna score já existe
            print("1. Verificando se a coluna 'score' já existe...")
            
            if check_column_exists(connection, 'training_data', 'score'):
                print("   ✅ Coluna 'score' já existe na tabela training_data")
            else:
                print("   ➕ Adicionando coluna 'score' na tabela training_data...")
                
                # Adicionar coluna score
                connection.execute(text("""
                    ALTER TABLE training_data 
                    ADD COLUMN IF NOT EXISTS score DECIMAL(3,2) DEFAULT 0.0
                """))
                
                print("   ✅ Coluna 'score' adicionada com sucesso")
            
            # 2. Atualizar scores existentes baseado no status
            print("2. Atualizando scores baseado no status...")
            
            result = connection.execute(text("""
                UPDATE training_data 
                SET score = CASE 
                    WHEN status = 'APPROVED' THEN 4.5
                    WHEN status = 'PENDING' THEN 3.0
                    WHEN status = 'REJECTED' THEN 1.0
                    ELSE 2.5
                END
                WHERE score IS NULL OR score = 0.0
            """))
            
            print(f"   ✅ {result.rowcount} registros atualizados com scores")
            
            # 3. Verificar outras colunas que podem estar faltando
            print("3. Verificando outras colunas necessárias...")
            
            required_columns = {
                'validation_score': 'DECIMAL(3,2) DEFAULT 0.0',
                'processing_logs': 'TEXT',
                'embedding': 'TEXT'
            }
            
            for col_name, col_def in required_columns.items():
                if not check_column_exists(connection, 'training_data', col_name):
                    print(f"   ➕ Adicionando coluna '{col_name}'...")
                    connection.execute(text(f"""
                        ALTER TABLE training_data 
                        ADD COLUMN IF NOT EXISTS {col_name} {col_def}
                    """))
                else:
                    print(f"   ✅ Coluna '{col_name}' já existe")
            
            # 4. Criar índices para performance
            print("4. Criando índices para melhor performance...")
            
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_training_data_status ON training_data(status)",
                "CREATE INDEX IF NOT EXISTS idx_training_data_score ON training_data(score DESC)",
                "CREATE INDEX IF NOT EXISTS idx_training_data_created_at ON training_data(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_training_data_content_search ON training_data USING gin(to_tsvector('portuguese', content))"
            ]
            
            for index_sql in indices:
                try:
                    connection.execute(text(index_sql))
                    print(f"   ✅ Índice criado: {index_sql.split('idx_')[1].split(' ')[0] if 'idx_' in index_sql else 'gin_content'}")
                except Exception as e:
                    print(f"   ⚠️  Índice já existe ou erro: {str(e)[:50]}...")
            
            # 5. Verificar estatísticas finais
            print("5. Verificando estatísticas da tabela...")
            
            stats = connection.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN status = 'APPROVED' THEN 1 END) as approved,
                    COUNT(CASE WHEN score > 0 THEN 1 END) as with_score,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(score) as min_score
                FROM training_data
            """)).fetchone()
            
            if stats:
                print(f"   📊 Total de registros: {stats.total_records}")
                print(f"   📊 Aprovados: {stats.approved}")
                print(f"   📊 Com score: {stats.with_score}")
                print(f"   📊 Score médio: {stats.avg_score:.2f}" if stats.avg_score else "   📊 Score médio: 0.00")
                print(f"   📊 Score máximo: {stats.max_score}")
                print(f"   📊 Score mínimo: {stats.min_score}")
            
            # Commit das alterações
            trans.commit()
            print("\n🎉 SCHEMA CORRIGIDO COM SUCESSO!")
            print("   Agora o sistema de treinamento deve funcionar completamente.")
            
            return True
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ ERRO durante a correção: {e}")
            return False
            
        finally:
            connection.close()
            
    except Exception as e:
        print(f"\n❌ ERRO na conexão: {e}")
        return False


def test_fixed_schema():
    """Testa se o schema foi corrigido corretamente"""
    
    print("\n🧪 TESTANDO SCHEMA CORRIGIDO")
    print("=" * 30)
    
    try:
        if 'create_app' in globals():
            app = create_app()
            with app.app_context():
                connection = db.engine.connect()
        else:
            connection = engine.connect()
        
        try:
            # Testar query que estava falhando
            result = connection.execute(text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'APPROVED' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                    COUNT(CASE WHEN file_path IS NOT NULL THEN 1 END) as file_uploads,      
                    COUNT(CASE WHEN title IS NOT NULL THEN 1 END) as text_entries,
                    AVG(score) as avg_score
                FROM training_data
            """)).fetchone()
            
            if result:
                print("✅ Query de estatísticas funcionando!")
                print(f"   Total: {result.total}, Aprovados: {result.approved}")
                print(f"   Score médio: {result.avg_score:.2f}" if result.avg_score else "   Score médio: 0.00")
            
            # Testar busca com score
            result2 = connection.execute(text("""
                SELECT id, title, content, score 
                FROM training_data 
                WHERE status = 'APPROVED' 
                ORDER BY score DESC 
                LIMIT 3
            """)).fetchall()
            
            print(f"✅ Busca por score funcionando! Encontrados {len(result2)} registros")
            
            return True
            
        finally:
            connection.close()
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


if __name__ == "__main__":
    print("🚀 INICIANDO CORREÇÃO DO BANCO DE DADOS")
    print("Este script irá adicionar a coluna 'score' e corrigir o schema")
    print()
    
    # Executar correção
    success = add_score_column()
    
    if success:
        # Testar correção
        test_success = test_fixed_schema()
        
        if test_success:
            print("\n✅ CORREÇÃO COMPLETA E VALIDADA!")
            print("Agora você pode executar novamente os testes:")
            print("python test_complete_training_system.py")
        else:
            print("\n⚠️  Correção aplicada mas testes falharam")
    else:
        print("\n❌ FALHA NA CORREÇÃO")
        print("Verifique a conexão com o banco de dados")
    
    print("\n" + "="*50)