#!/usr/bin/env python3
"""
Teste para validar as melhorias no sistema de AI
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_prompt_manager():
    """Testa o sistema de prompts refinado"""
    print("🧪 Testando AIPromptManager...")
    
    try:
        from app.services.ai_prompt import AIPromptManager
        
        pm = AIPromptManager()
        
        # Teste 1: Resposta fallback para diferentes níveis
        print("\n📝 Testando respostas fallback:")
        for risk in ['low', 'moderate', 'high', 'critical']:
            responses = pm.get_fallback_responses(risk, {'name': 'João'})
            print(f"  {risk}: {len(responses)} respostas - Exemplo: '{responses[0][:60]}...'")
        
        # Teste 2: Construção de prompt
        print("\n🔨 Testando construção de prompt:")
        prompt = pm.build_conversation_prompt(
            user_message="Estou me sentindo muito triste hoje",
            risk_level="moderate",
            provider="openai",
            user_context={'name': 'Maria'},
            is_first_message=True
        )
        
        print(f"  Mensagens: {len(prompt['messages'])}")
        print(f"  Temperature: {prompt['temperature']}")
        print(f"  Max tokens: {prompt['max_tokens']}")
        
        # Teste 3: Análise de humor da conversa
        print("\n🎭 Testando análise de humor:")
        history = [
            {'message_type': 'USER', 'content': 'não aguento mais'},
            {'message_type': 'AI', 'content': 'estou aqui para te apoiar'},
            {'message_type': 'USER', 'content': 'obrigado, me sinto melhor'},
        ]
        
        mood = pm._analyze_conversation_mood(history)
        print(f"  Humor detectado: {mood}")
        
        adaptations = pm._get_adaptation_rules(mood, 'moderate')
        print(f"  Adaptações: {adaptations[:100]}...")
        
        print("✅ AIPromptManager funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no AIPromptManager: {e}")
        return False

def test_ai_service():
    """Testa o serviço de AI refinado"""
    print("\n🤖 Testando AIService...")
    
    try:
        from app.services.ai_service import AIService
        
        ai = AIService()
        
        # Teste 1: Análise de sentimento básica
        print("\n💭 Testando análise de sentimento:")
        text = "Estou muito triste e não vejo esperança"
        sentiment = ai.analyze_sentiment(text)
        
        print(f"  Texto: '{text}'")
        print(f"  Score: {sentiment['score']}")
        print(f"  Emoção: {sentiment['emotion']}")
        print(f"  Intensidade: {sentiment['intensity']}")
        
        # Teste 2: Avaliação de risco
        print("\n⚠️ Testando avaliação de risco:")
        risk_level = ai.assess_risk_level(text, sentiment)
        print(f"  Nível de risco: {risk_level}")
        
        # Teste 3: Análise completa
        print("\n🔍 Testando análise completa:")
        analysis = ai.analyze_with_risk_assessment(text)
        print(f"  Score: {analysis['score']}")
        print(f"  Risco: {analysis['risk_level']}")
        print(f"  Requer atenção: {analysis['requires_attention']}")
        
        # Teste 4: Análise de entrada de diário
        print("\n📔 Testando análise de diário:")
        diary_text = "Hoje foi um dia difícil no trabalho. Me senti ansioso e com medo de não conseguir completar as tarefas."
        diary_analysis = ai.analyze_diary_entry(diary_text)
        
        if diary_analysis:
            print(f"  Emoções detectadas: {diary_analysis['detected_emotions']}")
            print(f"  Temas principais: {diary_analysis['main_themes']}")
            print(f"  Indicadores de risco: {diary_analysis['risk_indicators']}")
        
        # Teste 5: Resposta fallback
        print("\n💬 Testando resposta fallback:")
        response = ai.generate_response(
            user_message="Estou triste",
            risk_level="moderate",
            user_context={'name': 'Ana'}
        )
        
        print(f"  Resposta: '{response['message']}'")
        print(f"  Fonte: {response['source']}")
        print(f"  Confiança: {response['confidence']}")
        
        print("✅ AIService funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no AIService: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Testa integração entre os componentes"""
    print("\n🔗 Testando integração dos componentes...")
    
    try:
        from app.services.ai_service import create_ai_service
        from app.services.ai_prompt import create_prompt_manager
        
        # Criar instâncias
        ai_service = create_ai_service()
        prompt_manager = create_prompt_manager()
        
        # Verificar se estão conectados
        assert ai_service.prompt_manager is not None
        print("✅ Integração entre AIService e AIPromptManager: OK")
        
        # Testar fluxo completo
        user_message = "Me sinto perdido e sem rumo na vida"
        
        # 1. Análise de sentimento e risco
        analysis = ai_service.analyze_with_risk_assessment(user_message)
        print(f"✅ Análise completa: {analysis['emotion']} ({analysis['risk_level']})")
        
        # 2. Geração de resposta
        response = ai_service.generate_response(
            user_message=user_message,
            risk_level=analysis['risk_level'],
            user_context={'name': 'Carlos'}
        )
        print(f"✅ Resposta gerada: {len(response['message'])} caracteres")
        
        # Verificar características da resposta
        message = response['message'].lower()
        
        # Deve ser curta (objetivo)
        word_count = len(response['message'].split())
        assert word_count <= 60, f"Resposta muito longa: {word_count} palavras"
        print(f"✅ Resposta concisa: {word_count} palavras")
        
        # Não deve ter frases problemáticas
        problematic_phrases = [
            'me apresento', 'sou íris', 'me desculpo', 
            'entendo que', 'sei que é difícil', 'lamento que'
        ]
        
        has_problems = any(phrase in message for phrase in problematic_phrases)
        if not has_problems:
            print("✅ Resposta sem frases problemáticas")
        else:
            print("⚠️  Resposta contém frases a melhorar")
        
        print("✅ Integração funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de AI refinado\n")
    
    results = []
    
    # Executar testes
    results.append(("AIPromptManager", test_prompt_manager()))
    results.append(("AIService", test_ai_service()))
    results.append(("Integração", test_integration()))
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name:<20} {status}")
    
    print(f"\n🎯 Resultado final: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes passaram! Sistema refinado com sucesso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os problemas acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
