#!/usr/bin/env python3
"""
Script para verificar o status do sistema de treinamento da IA
"""

from app import create_app, db
from app.services.ai_service import AIService
from app.services.training_service import AITrainingService
from app.models import TrainingData, TrainingDataStatus
from sqlalchemy import text

def main():
    app = create_app()
    with app.app_context():
        print("=== ANÁLISE COMPLETA DO SISTEMA DE TREINAMENTO ===\n")
        
        # 1. Verificar configuração da IA
        print("1. CONFIGURAÇÃO DO AI SERVICE:")
        ai_service = AIService()
        stats = ai_service.get_service_statistics()
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        
        # 2. Verificar modelos disponíveis
        print("\n2. MODELOS CONFIGURADOS:")
        models = ai_service.get_model_info()
        for model in models:
            status_icon = "✅" if model['status'] == 'active' else "❌" if model['status'] == 'inactive' else "⚠️"
            print(f"   {status_icon} {model['provider']} ({model['model']}): {model['status']}")
        
        # 3. Verificar dados de treinamento manuais
        print("\n3. DADOS DE TREINAMENTO MANUAIS:")
        try:
            total_training = TrainingData.query.count()
            approved_training = TrainingData.query.filter_by(status=TrainingDataStatus.APPROVED).count()
            pending_training = TrainingData.query.filter_by(status=TrainingDataStatus.PENDING).count()
            processed_training = TrainingData.query.filter_by(status=TrainingDataStatus.PROCESSED).count()
            
            print(f"   - Total de dados submetidos: {total_training}")
            print(f"   - Dados aprovados: {approved_training}")
            print(f"   - Dados pendentes: {pending_training}")
            print(f"   - Dados processados: {processed_training}")
            
            if total_training == 0:
                print("   ⚠️  NENHUM DADO DE TREINAMENTO MANUAL ENCONTRADO")
        except Exception as e:
            print(f"   ❌ Erro ao verificar training_data: {e}")
        
        # 4. Verificar dados de conversas (treinamento automático)
        print("\n4. DADOS DE CONVERSAS (TREINAMENTO AUTOMÁTICO):")
        try:
            # Sessões totais
            total_sessions = db.session.execute(text("SELECT COUNT(*) FROM chat_sessions")).scalar()
            
            # Sessões bem avaliadas
            good_sessions = db.session.execute(text("""
                SELECT COUNT(*) FROM chat_sessions 
                WHERE user_rating >= 4
            """)).scalar()
            
            # Mensagens totais
            total_messages = db.session.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar()
            
            # Mensagens de usuário
            user_messages = db.session.execute(text("""
                SELECT COUNT(*) FROM chat_messages 
                WHERE message_type = 'USER'
            """)).scalar()
            
            print(f"   - Total de sessões de chat: {total_sessions}")
            print(f"   - Sessões bem avaliadas (4-5⭐): {good_sessions}")
            print(f"   - Total de mensagens: {total_messages}")
            print(f"   - Mensagens de usuários: {user_messages}")
            
            if good_sessions == 0:
                print("   ⚠️  NENHUMA SESSÃO BEM AVALIADA PARA TREINAMENTO AUTOMÁTICO")
            else:
                print(f"   ✅ {good_sessions} sessões disponíveis para treinamento RAG")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar conversas: {e}")
        
        # 5. Verificar sistema de embeddings
        print("\n5. SISTEMA DE EMBEDDINGS (RAG):")
        try:
            embedding_count = db.session.execute(text("SELECT COUNT(*) FROM conversation_embeddings")).scalar()
            print(f"   - Embeddings armazenados: {embedding_count}")
            
            if embedding_count == 0:
                print("   ⚠️  NENHUM EMBEDDING PROCESSADO")
                print("   💡 Execute training_service.train_from_successful_conversations() para processar")
            else:
                print(f"   ✅ {embedding_count} embeddings disponíveis para RAG")
                
        except Exception as e:
            print("   ❌ Tabela conversation_embeddings não existe")
            print("   💡 Execute training_service.setup_embeddings_table() para criar")
        
        # 6. Como a IA está usando os treinamentos
        print("\n6. COMO A IA USA OS DADOS:")
        print("   📝 Dados manuais (training_data):")
        print("      - Armazenados com embeddings vetoriais")
        print("      - Status: pending → approved → processed")
        print("      - Usado via RAG para contexto relevante")
        print()
        print("   🤖 Dados automáticos (conversas):")
        print("      - Sessões bem avaliadas (4-5⭐)")
        print("      - Processadas em embeddings")
        print("      - Busca por similaridade semântica")
        print("      - Sugestões contextualizadas")
        print()
        print("   ⚙️  Sistema RAG ativo:")
        print(f"      - Status: {'✅ ATIVO' if ai_service.rag_enabled else '❌ INATIVO'}")
        print("      - Busca conversas similares bem-sucedidas")
        print("      - Fornece contexto para respostas mais eficazes")
        
        # 7. Resumo do status
        print("\n" + "="*60)
        print("📊 RESUMO DO STATUS:")
        
        # Status geral
        if total_training > 0 or good_sessions > 0:
            print("✅ SISTEMA DE TREINAMENTO: FUNCIONANDO")
        else:
            print("⚠️  SISTEMA DE TREINAMENTO: SEM DADOS")
        
        # RAG
        if ai_service.rag_enabled:
            print("✅ SISTEMA RAG: ATIVO")
        else:
            print("❌ SISTEMA RAG: INATIVO")
        
        # IA
        active_models = len([m for m in models if m['status'] == 'active'])
        if active_models > 0:
            print(f"✅ MODELOS DE IA: {active_models} ATIVOS")
        else:
            print("❌ MODELOS DE IA: NENHUM ATIVO (apenas fallback)")
        
        print("="*60)

if __name__ == "__main__":
    main()
