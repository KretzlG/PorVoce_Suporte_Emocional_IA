#!/usr/bin/env python
"""
Script para adicionar colunas missing na tabela triage_logs
"""

import os
import sys
from sqlalchemy import text

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import create_app, db

def add_missing_columns():
    """Adiciona colunas que podem estar faltando na tabela triage_logs"""
    app = create_app()
    
    with app.app_context():
        try:
            # Lista de colunas para adicionar
            columns_to_add = [
                "ALTER TABLE triage_logs ADD COLUMN IF NOT EXISTS emotional_state VARCHAR(100);",
                "ALTER TABLE triage_logs ADD COLUMN IF NOT EXISTS notes TEXT;", 
                "ALTER TABLE triage_logs ADD COLUMN IF NOT EXISTS volunteer_assigned INTEGER;"
            ]
            
            for sql in columns_to_add:
                try:
                    print(f"Executando: {sql}")
                    db.session.execute(text(sql))
                    db.session.commit()
                    print("✅ Coluna adicionada com sucesso")
                except Exception as e:
                    print(f"⚠️  Aviso: {e}")
                    db.session.rollback()
                    # Continuar com as próximas colunas
            
            print("\n🎉 Migração concluída!")
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_missing_columns()
