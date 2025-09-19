#!/usr/bin/env python3
"""
Teste Integrado: IA + Sistema de Triagem (OpenAI + Fallbacks)
Valida todo o fluxo de detecção de risco e direcionamento para triagem interna
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.risk_analyzer import RiskAnalyzer
from app.services.ai_prompt import AIPromptManager
from app.services.ai_service import AIService
import json

def test_integrated_system():
    """Testa integração completa entre IA (OpenAI + Fallback) e sistema de triagem"""
    
    print("🔄 TESTE INTEGRADO: IA COMPLETA + TRIAGEM INTERNA")
    print("📡 Testando OpenAI + Fallbacks + Triagem")
    print("=" * 60)
    
    # Inicializar componentes
    risk_analyzer = RiskAnalyzer()
    prompt_manager = AIPromptManager()
    ai_service = AIService()
    
    # Verificar se OpenAI está disponível
    openai_available = ai_service.openai_client is not None
    print(f"🤖 OpenAI disponível: {'✅ SIM' if openai_available else '❌ NÃO (usando fallback)'}")
    
    # Casos de teste com diferentes níveis de risco
    test_cases = [
        {
            'message': 'quero morrer, não aguento mais',
            'expected_risk': 'critical',
            'scenario': 'Ideação suicida explícita'
        },
        {
            'message': 'não vejo sentido em nada, só atrapalho todo mundo',
            'expected_risk': 'critical', 
            'scenario': 'Desesperança com indicadores sutis'
        },
        {
            'message': 'estou muito triste e ansioso ultimamente',
            'expected_risk': 'moderate',
            'scenario': 'Ansiedade e tristeza moderada'
        },
        {
            'message': 'me sinto bem hoje, obrigado pela conversa',
            'expected_risk': 'low',
            'scenario': 'Estado emocional positivo'
        },
        {
            'message': 'preciso de ajuda para controlar minha ansiedade',
            'expected_risk': 'moderate',
            'scenario': 'Pedido de ajuda para ansiedade'
        }
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 TESTE {i}/{total_tests}: {case['scenario']}")
        print(f"Mensagem: \"{case['message']}\"")
        
        # 1. ANÁLISE COMPLETA COM IA SERVICE (OpenAI + Fallback)
        try:
            if openai_available:
                # Usar análise completa com OpenAI
                full_analysis = ai_service.analyze_with_risk_assessment(case['message'])
                detected_risk = full_analysis.get('risk_level', 'low')
                source = full_analysis.get('source', 'unknown')
                print(f"🤖 Análise completa (OpenAI): {detected_risk} [fonte: {source}]")
            else:
                # Fallback para sistema local
                full_analysis = None
                detected_risk = ai_service.assess_risk_level(case['message'])
                print(f"🔧 Análise fallback (local): {detected_risk}")
        except Exception as e:
            print(f"⚠️ Erro na análise OpenAI, usando fallback: {e}")
            detected_risk = ai_service.assess_risk_level(case['message'])
            full_analysis = None
        
        # 2. ANÁLISE LOCAL PARA COMPARAÇÃO
        local_analysis = risk_analyzer.analyze_message(case['message'])
        local_risk = local_analysis['risk_level']
        print(f"🏠 Análise local: {local_risk}")
        
        # 3. GERAÇÃO DE RESPOSTA INTEGRADA
        try:
            if openai_available:
                response_data = ai_service.generate_response(
                    user_message=case['message'],
                    risk_level=detected_risk,
                    fallback=True
                )
                ai_response = response_data.get('message', 'Erro na resposta')
                response_source = response_data.get('source', 'unknown')
                print(f"💬 Resposta gerada [{response_source}]: \"{ai_response[:100]}...\"")
            else:
                ai_response = "Análise em modo fallback"
                response_source = "fallback"
        except Exception as e:
            print(f"⚠️ Erro na geração de resposta: {e}")
            ai_response = "Erro na resposta"
            response_source = "error"
        
        # 4. RECOMENDAÇÕES DE TRIAGEM
        recommendations = local_analysis['recommendations']
        
        # 5. PROMPTS ADEQUADOS
        fallback_responses = prompt_manager.get_fallback_responses(detected_risk)
        
        # 6. VALIDAÇÕES INTEGRADAS
        # Verificar se risco foi detectado corretamente
        risk_correct = detected_risk == case['expected_risk']
        
        # Verificar se recomendações focam em triagem interna (apenas para casos de risco)
        internal_triage_mentioned = any(
            'triagem' in rec.lower() or 
            'nossa equipe' in rec.lower() or 
            'profissional' in rec.lower() and 'cvv' not in rec.lower() and '188' not in rec.lower()
            for rec in recommendations
        )
        
        # Verificar se respostas não mencionam CVV/188
        no_external_refs = not any(
            'cvv' in resp.lower() or '188' in resp.lower()
            for resp in fallback_responses + [ai_response]
        )
        
        # Verificar se respostas mencionam triagem interna (apenas para casos de risco)
        internal_mentioned = any(
            'triagem' in resp.lower() or 
            'nossa equipe' in resp.lower() or
            'equipe especializada' in resp.lower()
            for resp in fallback_responses + [ai_response]
        )
        
        # Para casos LOW RISK, é OK não mencionar triagem
        if detected_risk == 'low':
            internal_triage_mentioned = True  # Não exigir triagem para low risk
            internal_mentioned = True  # Não exigir menção à triagem para low risk
        
        # Verificar consistência entre análises
        risk_consistency = abs(
            ['low', 'moderate', 'high', 'critical'].index(detected_risk) - 
            ['low', 'moderate', 'high', 'critical'].index(local_risk)
        ) <= 1  # Diferença máxima de 1 nível
        
        print(f"✅ Risco correto: {risk_correct}")
        print(f"✅ Consistência OpenAI/Local: {risk_consistency}")
        print(f"✅ Triagem interna mencionada: {internal_triage_mentioned}")
        print(f"✅ Sem referências externas: {no_external_refs}")
        print(f"✅ Triagem interna nas respostas: {internal_mentioned}")
        
        # Exibir algumas recomendações e respostas
        print(f"📋 Principais recomendações:")
        for rec in recommendations[:3]:
            print(f"   • {rec}")
        
        print(f"💬 Exemplo de resposta fallback:")
        print(f"   \"{fallback_responses[0] if fallback_responses else 'Nenhuma resposta disponível'}\"")
        
        # Avaliar teste
        test_passed = (risk_correct and internal_triage_mentioned and 
                      no_external_refs and internal_mentioned and risk_consistency)
        
        if test_passed:
            passed_tests += 1
            print("✅ TESTE PASSOU")
        else:
            print("❌ TESTE FALHOU")
            if not risk_correct:
                print(f"   🔍 Risco esperado: {case['expected_risk']}, detectado: {detected_risk}")
            if not risk_consistency:
                print(f"   🔍 Inconsistência: OpenAI={detected_risk}, Local={local_risk}")
            if not internal_triage_mentioned:
                print("   🔍 Triagem interna não mencionada nas recomendações")
            if not no_external_refs:
                print("   🔍 Ainda há referências externas (CVV/188)")
            if not internal_mentioned:
                print("   🔍 Triagem interna não mencionada nas respostas")
    
    # RESULTADOS FINAIS
    print("\n" + "=" * 60)
    print(f"🏆 RESULTADOS FINAIS: {passed_tests}/{total_tests} testes passaram")
    print(f"📊 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 SISTEMA TOTALMENTE INTEGRADO E FUNCIONANDO!")
        print("✅ IA detecta riscos corretamente (OpenAI + Fallback)")
        print("✅ Sistema direciona para triagem interna")
        print("✅ Não há referências a serviços externos")
        print("✅ Respostas focam na plataforma interna")
        print("✅ Consistência entre diferentes análises")
    else:
        print("⚠️ Sistema precisa de ajustes:")
        failed_tests = total_tests - passed_tests
        print(f"❌ {failed_tests} teste(s) falharam")
    
    # TESTE ADICIONAL: Fallback quando OpenAI falha
    print(f"\n🔧 TESTE ADICIONAL: Robustez do Fallback")
    try:
        # Simular falha da OpenAI forçando erro
        fallback_response = ai_service._generate_response_fallback(
            "estou em crise", "high", {"name": "Usuário"}, ["Erro simulado"]
        )
        fallback_ok = ('cvv' not in fallback_response['message'].lower() and 
                      '188' not in fallback_response['message'].lower())
        print(f"✅ Fallback sem referências externas: {fallback_ok}")
        if not fallback_ok:
            print(f"   🔍 Resposta fallback: {fallback_response['message']}")
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = test_integrated_system()
    exit(0 if success else 1)
