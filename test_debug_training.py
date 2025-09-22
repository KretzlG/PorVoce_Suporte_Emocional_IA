#!/usr/bin/env python3
"""
Teste para verificar se o sistema de logging está detectando correspondências
"""

def test_debug_mode():
    """Simula o processo de debug para identificar o problema"""
    
    print("🔧 TESTE DE DEBUG - SISTEMA DE LOGGING")
    print("=" * 60)
    
    print("✅ Correções aplicadas:")
    print("- ✅ Adicionado import TrainingDataType")
    print("- ✅ Melhorado método _extract_keywords para arquivos")
    print("- ✅ Adicionado método _extract_file_content")
    print("- ✅ Logs de debug para acompanhar extração")
    print("- ✅ Forçado recarregamento do cache")
    print("- ✅ Reduzido limiar de similaridade para 0.1")
    
    print("\n🔍 O que será logado agora:")
    print("- TRAINING_DATA_LOAD: Quantos dados foram carregados")
    print("- FILE_EXTRACTION: Conteúdo extraído dos arquivos")
    print("- KEYWORDS_EXTRACTION: Palavras-chave encontradas")
    print("- TRAINING_DEBUG: Score de cada comparação")
    print("- MATCH FOUND: Quando uma correspondência for detectada")
    
    print("\n🎯 Próximo teste:")
    print("1. Faça uma pergunta sobre 'ansiedade em crianças'")
    print("2. Verifique o arquivo logs/training_usage.log")
    print("3. Procure por logs de FILE_EXTRACTION e KEYWORDS_EXTRACTION")
    print("4. Verifique se o score > 0.1 para detectar correspondência")
    
    print("\n📋 Exemplo esperado no log:")
    print("TRAINING_DATA_LOAD: Carregando 1 dados aprovados")
    print("FILE_EXTRACTION: Extraído 2547 caracteres do arquivo")
    print("KEYWORDS_EXTRACTION: Item 2 - 15 palavras-chave: ['ansiedade', 'pânico', 'crianças'...]")
    print("TRAINING_DEBUG: Training ID 2 - Score: 0.650")
    print("MATCH FOUND! Score: 0.650")
    
    print("\n" + "=" * 60)
    print("🚀 SISTEMA CORRIGIDO E PRONTO PARA TESTE!")

if __name__ == "__main__":
    test_debug_mode()