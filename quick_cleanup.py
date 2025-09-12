#!/usr/bin/env python3
"""
Script rápido para limpar dados de teste
Remove apenas dados de chat e triagem, mantendo usuários
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def quick_cleanup():
    """Limpeza rápida para testes"""
    app = create_app()
    
    with app.app_context():
        try:
            # Limpar em ordem para evitar problemas de FK
            queries = [
                "DELETE FROM chat1a1_messages;",
                "DELETE FROM chat1a1_sessions;", 
                "DELETE FROM chat_messages;",
                "DELETE FROM chat_sessions;",
                "DELETE FROM triage_logs;",
            ]
            
            for query in queries:
                try:
                    db.session.execute(db.text(query))
                except Exception as e:
                    print(f"Erro em {query}: {e}")
            
            db.session.commit()
            print("✅ Dados de chat e triagem removidos!")
            print("👥 Usuários e voluntários mantidos.")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            db.session.rollback()

if __name__ == "__main__":
    quick_cleanup()
