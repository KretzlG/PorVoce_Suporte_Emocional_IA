#!/usr/bin/env python3
"""
Script para limpar o banco de dados mantendo apenas usuários
Remove todos os dados exceto:
- Estrutura das tabelas (schema)
- Tabela de usuários (users)
- Tabela de voluntários (volunteers) - para manter relacionamentos
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    ChatSession, ChatMessage, 
    Chat1a1Session, Chat1a1Message,
    TriageLog, TrainingData, User, Volunteer
)

def confirm_cleanup():
    """Confirmar se o usuário realmente quer limpar o banco"""
    print("⚠️  ATENÇÃO: Este script irá EXCLUIR TODOS OS DADOS do banco!")
    print("📋 Dados que serão MANTIDOS:")
    print("   - Usuários (tabela users)")
    print("   - Voluntários (tabela volunteers)")
    print("   - Estrutura das tabelas")
    print()
    print("🗑️  Dados que serão EXCLUÍDOS:")
    print("   - Todas as conversas de chat normal")
    print("   - Todas as sessões de chat 1a1")
    print("   - Todas as mensagens")
    print("   - Todos os logs de triagem")
    print("   - Todos os dados de treinamento")
    print()
    
    response = input("Tem certeza que deseja continuar? Digite 'CONFIRMAR' para prosseguir: ")
    return response.strip() == 'CONFIRMAR'

def cleanup_database():
    """Limpar dados do banco mantendo usuários"""
    try:
        print("🚀 Iniciando limpeza do banco de dados...")
        
        # Desabilitar verificações de foreign key temporariamente (PostgreSQL)
        db.session.execute(db.text("SET session_replication_role = replica;"))
        
        # Contar registros antes da limpeza
        counts_before = {
            'users': User.query.count(),
            'volunteers': Volunteer.query.count(),
            'chat_sessions': ChatSession.query.count(),
            'chat_messages': ChatMessage.query.count(),
            'chat1a1_sessions': Chat1a1Session.query.count(),
            'chat1a1_messages': Chat1a1Message.query.count(),
            'triage_logs': TriageLog.query.count(),
        }
        
        # Adicionar contagem de dados de treinamento se existir
        try:
            counts_before['training_data'] = TrainingData.query.count()
        except:
            counts_before['training_data'] = 0
        
        print(f"📊 Registros encontrados:")
        for table, count in counts_before.items():
            print(f"   {table}: {count}")
        print()
        
        # 1. Excluir mensagens de chat 1a1 (relacionadas às sessões)
        print("🗑️  Excluindo mensagens de chat 1a1...")
        Chat1a1Message.query.delete()
        db.session.commit()
        
        # 2. Excluir sessões de chat 1a1
        print("🗑️  Excluindo sessões de chat 1a1...")
        Chat1a1Session.query.delete()
        db.session.commit()
        
        # 3. Excluir mensagens de chat normal
        print("🗑️  Excluindo mensagens de chat normal...")
        ChatMessage.query.delete()
        db.session.commit()
        
        # 4. Excluir sessões de chat normal
        print("🗑️  Excluindo sessões de chat normal...")
        ChatSession.query.delete()
        db.session.commit()
        
        # 5. Excluir logs de triagem
        print("🗑️  Excluindo logs de triagem...")
        TriageLog.query.delete()
        db.session.commit()
        
        # 6. Excluir dados de treinamento (se existir)
        try:
            print("🗑️  Excluindo dados de treinamento...")
            TrainingData.query.delete()
            db.session.commit()
        except Exception as e:
            print(f"   ⚠️  Erro ao excluir dados de treinamento (pode não existir): {e}")
        
        # Reabilitar verificações de foreign key
        db.session.execute(db.text("SET session_replication_role = DEFAULT;"))
        db.session.commit()
        
        # Contar registros após limpeza
        counts_after = {
            'users': User.query.count(),
            'volunteers': Volunteer.query.count(),
            'chat_sessions': ChatSession.query.count(),
            'chat_messages': ChatMessage.query.count(),
            'chat1a1_sessions': Chat1a1Session.query.count(),
            'chat1a1_messages': Chat1a1Message.query.count(),
            'triage_logs': TriageLog.query.count(),
        }
        
        try:
            counts_after['training_data'] = TrainingData.query.count()
        except:
            counts_after['training_data'] = 0
        
        print("\n✅ Limpeza concluída com sucesso!")
        print(f"📊 Registros após limpeza:")
        for table, count in counts_after.items():
            print(f"   {table}: {count}")
        
        print(f"\n📈 Resumo da limpeza:")
        for table in counts_before:
            removed = counts_before[table] - counts_after[table]
            if removed > 0:
                print(f"   ❌ {table}: {removed} registros removidos")
            else:
                print(f"   ✅ {table}: {counts_after[table]} registros mantidos")
        
        print(f"\n🕐 Limpeza executada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Erro durante a limpeza: {e}")
        db.session.rollback()
        return False
    
    return True

def main():
    """Função principal"""
    print("🧹 Script de Limpeza do Banco de Dados - Por Você")
    print("=" * 50)
    
    if not confirm_cleanup():
        print("❌ Operação cancelada pelo usuário.")
        return
    
    # Criar aplicação Flask
    app = create_app()
    
    with app.app_context():
        success = cleanup_database()
        
        if success:
            print("\n🎉 Banco de dados limpo com sucesso!")
            print("💡 Todos os dados foram removidos, exceto usuários e voluntários.")
            print("🚀 Seu sistema está pronto para novos testes!")
        else:
            print("\n💥 Falha na limpeza do banco de dados.")
            print("🔍 Verifique os logs de erro acima.")

if __name__ == "__main__":
    main()
