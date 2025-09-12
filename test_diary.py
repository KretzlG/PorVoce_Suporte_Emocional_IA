#!/usr/bin/env python3
"""Teste simples do blueprint do diário"""

try:
    from app.routes.diary import diary
    print("✅ Blueprint do diário carregado com sucesso!")
    print(f"Nome do blueprint: {diary.name}")
    print(f"URL prefix: {diary.url_prefix}")
    
    # Testar as rotas
    rules = [rule for rule in diary.url_map.iter_rules() if rule.endpoint.startswith('diary')]
    print(f"Rotas disponíveis: {len(rules)}")
    for rule in rules:
        print(f"  - {rule.rule} -> {rule.endpoint}")
        
except ImportError as e:
    print(f"❌ Erro ao importar blueprint: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
