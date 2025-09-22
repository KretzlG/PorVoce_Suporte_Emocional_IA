"""
Script de Teste Completo do Sistema de Treinamento de IA
Testa todas as funcionalidades: RAG, Prompt Engineering, Fine-tuning
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from datetime import datetime
from app import create_app, db
from app.services.ai_service import AIService
from app.services.advanced_rag_service import advanced_rag_service
from app.services.advanced_prompt_engineer import advanced_prompt_engineer, PromptContext, RiskLevel
from app.services.finetuning_preparator import finetuning_preparator

def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(test_name, result, success=None):
    """Imprime resultado de teste formatado"""
    if success is None:
        success = result.get('success', True) if isinstance(result, dict) else bool(result)
    
    status = "✅ PASSOU" if success else "❌ FALHOU"
    print(f"{status} {test_name}")
    
    if isinstance(result, dict):
        if 'error' in result:
            print(f"   Erro: {result['error']}")
        elif not success:
            print(f"   Detalhes: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
    
    return success

def test_ai_service_basic():
    """Testa funcionalidades básicas do AIService"""
    print_header("TESTE: AIService Básico")
    
    try:
        ai_service = AIService()
        results = []
        
        # Teste 1: Análise de sentimento
        sentiment_result = ai_service.analyze_sentiment("Estou me sentindo muito ansioso e não sei o que fazer")
        results.append(print_result("Análise de Sentimento", sentiment_result))
        
        # Teste 2: Avaliação de risco
        risk_level = ai_service.assess_risk_level("Não aguento mais, quero que tudo acabe")
        results.append(print_result("Avaliação de Risco", {'risk_level': risk_level}, risk_level in ['high', 'critical']))
        
        # Teste 3: Análise completa
        complete_analysis = ai_service.analyze_with_risk_assessment("Tenho problemas no trabalho e isso me deixa triste")
        results.append(print_result("Análise Completa", complete_analysis))
        
        # Teste 4: Estatísticas do serviço
        stats = ai_service.get_service_statistics()
        results.append(print_result("Estatísticas do Serviço", stats))
        
        # Teste 5: Capacidades do sistema
        capabilities = ai_service.get_system_capabilities()
        results.append(print_result("Capacidades do Sistema", capabilities))
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste básico: {e}")
        return False

def test_advanced_rag():
    """Testa sistema RAG avançado"""
    print_header("TESTE: Sistema RAG Avançado")
    
    try:
        results = []
        
        # Teste 1: Busca de contexto avançado
        context_result = advanced_rag_service.get_enhanced_context(
            "Estou com ansiedade", 
            risk_level='moderate', 
            context_type='all'
        )
        results.append(print_result("Busca de Contexto RAG", context_result))
        
        # Teste 2: Estatísticas de dados de treinamento
        stats = advanced_rag_service.get_training_data_statistics()
        results.append(print_result("Estatísticas RAG", stats))
        
        # Teste 3: Busca em conteúdo de treinamento
        search_results = advanced_rag_service.search_training_content("ansiedade", limit=5)
        results.append(print_result("Busca em Conteúdo", {'results': search_results, 'count': len(search_results)}))
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste RAG: {e}")
        return False

def test_prompt_engineering():
    """Testa sistema de prompt engineering"""
    print_header("TESTE: Prompt Engineering Avançado")
    
    try:
        results = []
        
        # Teste 1: Estatísticas do prompt engineering
        stats = advanced_prompt_engineer.get_prompt_statistics()
        results.append(print_result("Estatísticas Prompt Engineering", stats))
        
        # Teste 2: Criar contexto de prompt
        context = PromptContext(
            user_message="Estou muito estressado com o trabalho",
            risk_level=RiskLevel.MODERATE,
            user_name="Usuário Teste"
        )
        
        # Teste 3: Validar contexto
        is_valid, errors = advanced_prompt_engineer.validate_prompt_context(context)
        results.append(print_result("Validação de Contexto", {'valid': is_valid, 'errors': errors}, is_valid))
        
        # Teste 4: Construir prompt contextualizado
        prompt_data = advanced_prompt_engineer.build_contextual_prompt(context, provider='openai')
        results.append(print_result("Construção de Prompt", prompt_data))
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste de prompt engineering: {e}")
        return False

def test_finetuning_preparation():
    """Testa preparação para fine-tuning"""
    print_header("TESTE: Preparação Fine-tuning")
    
    try:
        results = []
        
        # Teste 1: Recomendações de dataset
        recommendations = finetuning_preparator.get_dataset_recommendations()
        results.append(print_result("Recomendações Dataset", recommendations))
        
        # Teste 2: Criar dataset de conversas (pequeno para teste)
        conv_dataset = finetuning_preparator.create_conversation_dataset(
            format_type='openai_chat',
            max_samples=10
        )
        results.append(print_result("Dataset de Conversas", conv_dataset))
        
        # Teste 3: Criar dataset de dados de treinamento
        training_dataset = finetuning_preparator.create_training_data_dataset(
            format_type='jsonl',
            max_samples=5
        )
        results.append(print_result("Dataset de Treinamento", training_dataset))
        
        # Teste 4: Dataset híbrido
        hybrid_dataset = finetuning_preparator.create_hybrid_dataset(
            total_samples=15,
            format_type='openai_chat'
        )
        results.append(print_result("Dataset Híbrido", hybrid_dataset))
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste de fine-tuning: {e}")
        return False

def test_ai_response_generation():
    """Testa geração de respostas com sistema completo"""
    print_header("TESTE: Geração de Respostas Completa")
    
    try:
        ai_service = AIService()
        results = []
        
        # Casos de teste com diferentes níveis de risco
        test_cases = [
            {
                'message': 'Oi, estou me sentindo um pouco triste hoje',
                'risk': 'low',
                'name': 'Caso Baixo Risco'
            },
            {
                'message': 'Estou muito ansioso com meu trabalho e não consigo dormir',
                'risk': 'moderate',
                'name': 'Caso Risco Moderado'
            },
            {
                'message': 'Não aguento mais essa situação, me sinto desesperado',
                'risk': 'high',
                'name': 'Caso Alto Risco'
            }
        ]
        
        for case in test_cases:
            try:
                print(f"\\n🧪 Testando: {case['name']}")
                
                # Gerar resposta
                response = ai_service.generate_response(
                    user_message=case['message'],
                    risk_level=case['risk'],
                    user_context={'name': 'Teste'},
                    conversation_history=[]
                )
                
                success = bool(response.get('message'))
                results.append(print_result(case['name'], response, success))
                
                if success:
                    print(f"   Fonte: {response.get('source', 'N/A')}")
                    print(f"   RAG Usado: {response.get('rag_used', False)}")
                    print(f"   Confiança: {response.get('confidence', 0)}")
                    print(f"   Resposta: {response['message'][:100]}...")
                
            except Exception as e:
                print(f"   ❌ Erro no caso {case['name']}: {e}")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste de resposta: {e}")
        return False

def test_integration():
    """Testa integração entre todos os sistemas"""
    print_header("TESTE: Integração Completa")
    
    try:
        ai_service = AIService()
        results = []
        
        # Teste 1: Busca de contexto avançado via AI Service
        context_result = ai_service.get_advanced_context(
            "Como lidar com ansiedade?", 
            risk_level='moderate'
        )
        results.append(print_result("Contexto via AIService", context_result))
        
        # Teste 2: Análise de prompt via AI Service
        prompt_analysis = ai_service.analyze_prompt_context(
            "Estou me sentindo muito mal",
            risk_level='high',
            user_context={'name': 'Teste'}
        )
        results.append(print_result("Análise Prompt via AIService", prompt_analysis))
        
        # Teste 3: Busca de conteúdo via AI Service
        search_result = ai_service.search_training_content("depressão", limit=3)
        results.append(print_result("Busca Conteúdo via AIService", search_result))
        
        # Teste 4: Criar dataset via AI Service
        dataset_result = ai_service.create_finetuning_dataset(
            dataset_type='hybrid',
            format_type='jsonl',
            max_samples=5
        )
        results.append(print_result("Dataset via AIService", dataset_result))
        
        return all(results)
        
    except Exception as e:
        print(f"❌ ERRO no teste de integração: {e}")
        return False

def run_full_test_suite():
    """Executa suite completa de testes"""
    print_header("SUITE COMPLETA DE TESTES - SISTEMA DE TREINAMENTO IA")
    print(f"Iniciado em: {datetime.now().isoformat()}")
    
    # Criar aplicação Flask para contexto
    app = create_app()
    
    with app.app_context():
        test_results = {}
        
        # Executar todos os testes
        test_results['ai_service_basic'] = test_ai_service_basic()
        test_results['advanced_rag'] = test_advanced_rag()
        test_results['prompt_engineering'] = test_prompt_engineering()
        test_results['finetuning_preparation'] = test_finetuning_preparation()
        test_results['ai_response_generation'] = test_ai_response_generation()
        test_results['integration'] = test_integration()
        
        # Sumário dos resultados
        print_header("SUMÁRIO DOS RESULTADOS")
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{status} {test_name.replace('_', ' ').title()}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        print(f"\\n📊 RESULTADO FINAL: {passed}/{total} testes passaram ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 SISTEMA FUNCIONANDO ADEQUADAMENTE!")
            print("✨ Todos os componentes principais estão operacionais")
            print("🚀 Sistema pronto para uso em produção")
        elif success_rate >= 60:
            print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
            print("🔧 Algumas funcionalidades podem precisar de ajustes")
        else:
            print("🚨 SISTEMA COM PROBLEMAS CRÍTICOS")
            print("🛠️  Requer correções antes do uso")
        
        print(f"\\nTeste concluído em: {datetime.now().isoformat()}")
        
        return success_rate >= 80

if __name__ == "__main__":
    try:
        success = run_full_test_suite()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\\n💥 ERRO CRÍTICO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)