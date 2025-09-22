#!/usr/bin/env python3
"""
Teste específico para verificar detecção de correspondência de treinamento
"""

def test_specific_case():
    """Testa o caso específico da pergunta sobre síndrome do pânico"""
    print("🔍 TESTE ESPECÍFICO - DETECÇÃO DE CORRESPONDÊNCIA")
    print("=" * 60)
    
    user_question = "me explique A compreensão dos fatores que contribuem para o desenvolvimento da síndrome do pânico em crianças e adolescentes"
    
    ai_response = "Os fatores que contribuem para o desenvolvimento da síndrome do pânico em crianças e adolescentes podem incluir predisposição genética, histórico familiar, estresse, traumas emocionais e até mesmo problemas de saúde mental. É importante buscar ajuda profissional para entender melhor e lidar com essa condição."
    
    training_title = "Manejo de Crises de Ansiedade e Pânico em crianças e adolescentes: condições multifatoriais"
    
    print("📝 DADOS DO TESTE:")
    print(f"👤 Pergunta do usuário: {user_question}")
    print(f"🤖 Resposta da IA: {ai_response}")
    print(f"📄 Treinamento disponível: {training_title}")
    
    print("\n🔍 ANÁLISE DE PALAVRAS-CHAVE:")
    
    # Extrair palavras-chave do usuário
    user_words = set(user_question.lower().split())
    print(f"👤 Palavras do usuário: {sorted(user_words)}")
    
    # Extrair palavras-chave da resposta
    response_words = set(ai_response.lower().split())
    print(f"🤖 Palavras da resposta: {sorted(response_words)}")
    
    # Extrair palavras-chave do treinamento
    training_words = set(training_title.lower().split())
    print(f"📄 Palavras do treinamento: {sorted(training_words)}")
    
    print("\n🎯 CORRESPONDÊNCIAS ENCONTRADAS:")
    
    # Palavras-chave específicas importantes
    important_keywords = {
        'ansiedade', 'pânico', 'crianças', 'adolescentes', 'fatores', 
        'desenvolvimento', 'síndrome', 'condições', 'multifatoriais'
    }
    
    user_matches = user_words.intersection(training_words)
    response_matches = response_words.intersection(training_words)
    important_matches = (user_words | response_words).intersection(important_keywords)
    
    print(f"✅ Palavras da pergunta que coincidem com treinamento: {sorted(user_matches)}")
    print(f"✅ Palavras da resposta que coincidem com treinamento: {sorted(response_matches)}")
    print(f"🎯 Palavras-chave importantes detectadas: {sorted(important_matches)}")
    
    # Calcular similaridade
    total_matches = len(user_matches) + len(response_matches)
    important_match_score = len(important_matches) / len(important_keywords)
    
    print(f"\n📊 PONTUAÇÃO:")
    print(f"🔢 Total de correspondências: {total_matches}")
    print(f"🎯 Score de palavras importantes: {important_match_score:.3f}")
    print(f"📈 Score combinado estimado: {(total_matches * 0.1 + important_match_score * 0.5):.3f}")
    
    print("\n💡 DIAGNÓSTICO:")
    if total_matches >= 3 or important_match_score > 0.3:
        print("✅ DEVERIA SER DETECTADO - Há correspondência clara!")
        print("🔧 Se não foi detectado, verificar:")
        print("   - Se o arquivo foi processado corretamente")
        print("   - Se o conteúdo do arquivo contém as palavras-chave")
        print("   - Se o limiar de similaridade está muito alto")
    else:
        print("❌ BAIXA CORRESPONDÊNCIA - Pode não ser detectado")
        
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Verificar conteúdo real do arquivo de treinamento")
    print("2. Testar com limiar de similaridade mais baixo (0.1)")
    print("3. Adicionar mais palavras-chave específicas")
    print("4. Verificar se o cache está atualizado")

if __name__ == "__main__":
    test_specific_case()