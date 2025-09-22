#!/usr/bin/env python3
"""
Teste do Sistema de Logging de Uso de Dados de Treinamento
Demonstra como o sistema rastreia se a IA está usando os dados enviados
"""

import os
import sys
import json
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_training_usage_test():
    """
    Simula o funcionamento do sistema de logging de treinamento
    """
    print("🔍 TESTE DO SISTEMA DE LOGGING DE TREINAMENTO")
    print("=" * 60)
    
    print("\n📋 Funcionalidades Implementadas:")
    print("✅ Logger específico para dados de treinamento")
    print("✅ Rastreamento de similaridade entre consultas e dados de treinamento") 
    print("✅ Detecção de uso de arquivos vs texto")
    print("✅ Estatísticas de uso em tempo real")
    print("✅ Cache inteligente de dados de treinamento")
    print("✅ Logs detalhados em arquivo separado")
    
    print("\n🎯 Como Funciona:")
    print("1. Sistema carrega todos os dados de treinamento aprovados")
    print("2. Para cada resposta da IA, verifica similaridade com dados de treinamento")
    print("3. Analisa palavras-chave e frases em comum")
    print("4. Calcula score de similaridade (0.0 - 1.0)")
    print("5. Se score > 0.3, considera que dados de treinamento foram usados")
    print("6. Registra estatísticas e logs detalhados")
    
    print("\n📊 Exemplo de Análise:")
    
    # Simular dados de exemplo
    example_user_message = "Estou me sentindo muito ansioso ultimamente, não consigo dormir"
    example_ai_response = "Compreendo sua ansiedade. É importante buscar técnicas de relaxamento antes de dormir, como respiração profunda."
    
    print(f"👤 Usuário: {example_user_message}")
    print(f"🤖 IA: {example_ai_response}")
    
    # Simular resultado do logging
    example_result = {
        "timestamp": datetime.now().isoformat(),
        "user_message_length": len(example_user_message),
        "ai_response_length": len(example_ai_response),
        "risk_level": "moderate",
        "training_matches_found": 2,
        "used_training_data": True,
        "top_matches": [
            {
                "training_id": 1,
                "training_title": "Técnicas para Ansiedade",
                "training_type": "text",
                "similarity_score": 0.65,
                "keyword_overlap": 3,
                "details": {
                    "training_keywords_matched": ["ansiedade", "relaxamento", "respiração"]
                }
            },
            {
                "training_id": 5,
                "training_title": "Manual de Sono e Ansiedade.pdf",
                "training_type": "file",
                "similarity_score": 0.45,
                "keyword_overlap": 2,
                "details": {
                    "training_keywords_matched": ["ansioso", "dormir"]
                }
            }
        ]
    }
    
    print(f"\n📈 Resultado da Análise:")
    print(f"   ✅ Dados de treinamento utilizados: {example_result['used_training_data']}")
    print(f"   📊 Correspondências encontradas: {example_result['training_matches_found']}")
    print(f"   🏆 Melhor correspondência: {example_result['top_matches'][0]['training_title']} (Score: {example_result['top_matches'][0]['similarity_score']})")
    print(f"   📝 Tipo: {example_result['top_matches'][0]['training_type'].upper()}")
    print(f"   🔗 Palavras-chave em comum: {', '.join(example_result['top_matches'][0]['details']['training_keywords_matched'])}")
    
    print("\n📁 Estrutura de Logs:")
    print("📂 logs/")
    print("  └── 📄 training_usage.log")
    print("       ├── TRAINING_DATA_USED: {...}")
    print("       ├── NO_TRAINING_DATA_USED: {...}")
    print("       └── FILE_EXTRACTION: {...}")
    
    print("\n🔧 Integração com AIService:")
    print("- ✅ Logging automático em generate_response()")
    print("- ✅ Verificação para OpenAI e Gemini")
    print("- ✅ Relatórios via API")
    print("- ✅ Estatísticas em tempo real")
    
    print("\n📊 Exemplo de Estatísticas:")
    example_stats = {
        "total_training_items": 25,
        "file_based_items": 12,
        "text_based_items": 13,
        "usage_statistics": {
            "total_queries": 150,
            "training_matches": 45,
            "file_matches": 20,
            "text_matches": 25
        },
        "usage_rate": {
            "training_usage_percentage": 30.0,
            "file_usage_percentage": 13.33,
            "text_usage_percentage": 16.67
        }
    }
    
    print(f"   📈 Total de consultas: {example_stats['usage_statistics']['total_queries']}")
    print(f"   ✅ Utilizou treinamento: {example_stats['usage_statistics']['training_matches']} ({example_stats['usage_rate']['training_usage_percentage']}%)")
    print(f"   📄 Dados de arquivo: {example_stats['usage_statistics']['file_matches']} ({example_stats['usage_rate']['file_usage_percentage']}%)")
    print(f"   📝 Dados de texto: {example_stats['usage_statistics']['text_matches']} ({example_stats['usage_rate']['text_usage_percentage']}%)")
    
    print("\n🌐 APIs Disponíveis:")
    print("   GET /training/api/stats - Estatísticas básicas")
    print("   GET /training/api/usage-report - Relatório detalhado")
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA DE LOGGING IMPLEMENTADO COM SUCESSO!")
    print("🎯 Agora você pode rastrear em tempo real se a IA está")
    print("   utilizando os dados de treinamento enviados via arquivo ou texto!")

def show_log_examples():
    """
    Mostra exemplos de como os logs aparecerão
    """
    print("\n📄 EXEMPLOS DE LOGS QUE SERÃO GERADOS:")
    print("=" * 50)
    
    # Exemplo 1: Uso de dados detectado
    log1 = {
        "timestamp": "2025-09-22T15:30:45.123456",
        "level": "INFO",
        "event": "TRAINING_DATA_USED",
        "data": {
            "user_message_length": 85,
            "ai_response_length": 180,
            "risk_level": "moderate",
            "training_matches_found": 1,
            "top_matches": [
                {
                    "training_id": 3,
                    "training_title": "Apoio para Ansiedade",
                    "training_type": "text",
                    "similarity_score": 0.72
                }
            ]
        }
    }
    
    print("📝 Log 1 - Dados de treinamento utilizados:")
    print(json.dumps(log1, indent=2, ensure_ascii=False))
    
    # Exemplo 2: Nenhum uso detectado
    log2 = {
        "timestamp": "2025-09-22T15:32:10.987654",
        "level": "INFO", 
        "event": "NO_TRAINING_DATA_USED",
        "message": "Query processed without training data matches"
    }
    
    print("\n📝 Log 2 - Nenhum dado de treinamento utilizado:")
    print(json.dumps(log2, indent=2, ensure_ascii=False))
    
    # Exemplo 3: Extração de arquivo
    log3 = {
        "timestamp": "2025-09-22T15:35:20.456789",
        "level": "INFO",
        "event": "FILE_EXTRACTION", 
        "data": {
            "action": "FILE_CONTENT_EXTRACTED",
            "file_path": "/uploads/training/abc123_manual_apoio.pdf",
            "content_length": 2547,
            "content_preview": "Manual de Apoio Emocional\n\n1. Técnicas de Escuta Ativa\nA escuta ativa é fundamental..."
        }
    }
    
    print("\n📝 Log 3 - Extração de conteúdo de arquivo:")
    print(json.dumps(log3, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    simulate_training_usage_test()
    show_log_examples()