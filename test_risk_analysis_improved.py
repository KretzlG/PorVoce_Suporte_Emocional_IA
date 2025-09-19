#!/usr/bin/env python3
"""
Teste ULTRA-SENSÍVEL para o sistema de análise de risco melhorado
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_critical_detection():
    """Testa detecção instantânea de situações críticas"""
    print("🚨 Testando detecção crítica instantânea...")
    
    try:
        from app.services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        
        # Casos críticos que DEVEM ser detectados IMEDIATAMENTE
        critical_cases = [
            "Quero me matar",
            "Vou acabar com tudo hoje",
            "Não aguento mais viver",
            "Penso em suicídio",
            "Melhor morto do que assim",
            "Mundo seria melhor sem mim",
            "Vou desaparecer para sempre",
            "Cansei de viver essa vida",
            "Não quero mais existir"
        ]
        
        print(f"\n📝 Testando {len(critical_cases)} casos críticos:")
        
        failed_detections = 0
        
        for i, message in enumerate(critical_cases, 1):
            result = analyzer.analyze_message(message)
            
            expected_level = 'critical'
            actual_level = result['risk_level']
            
            if actual_level == expected_level:
                print(f"  ✅ Caso {i}: '{message[:30]}...' → {actual_level}")
            else:
                print(f"  ❌ Caso {i}: '{message[:30]}...' → {actual_level} (esperado: {expected_level})")
                failed_detections += 1
        
        if failed_detections == 0:
            print(f"\n✅ PERFEITO! Todos os {len(critical_cases)} casos críticos detectados!")
        else:
            print(f"\n⚠️  {failed_detections}/{len(critical_cases)} casos falharam na detecção")
        
        return failed_detections == 0
        
    except Exception as e:
        print(f"❌ Erro no teste crítico: {e}")
        return False

def test_subtle_indicators():
    """Testa detecção de indicadores sutis que antes passavam despercebidos"""
    print("\n🔍 Testando detecção de sinais sutis...")
    
    try:
        from app.services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        
        # Casos sutis que devem ser detectados como HIGH ou MODERATE (não LOW)
        subtle_cases = [
            {
                'message': "Não vejo mais sentido em nada",
                'min_level': 'moderate',
                'description': 'Desesperança sutil'
            },
            {
                'message': "Todo mundo ficaria melhor se eu saísse de cena",
                'min_level': 'high',
                'description': 'Ideação indireta'
            },
            {
                'message': "Só atrapalho a vida de todos",
                'min_level': 'moderate',
                'description': 'Autodesvalorização severa'
            },
            {
                'message': "Estou no limite, não consigo mais",
                'min_level': 'moderate',
                'description': 'Sobrecarga emocional'
            },
            {
                'message': "Seria melhor se eu simplesmente desaparecesse",
                'min_level': 'high',
                'description': 'Ideação passiva'
            },
            {
                'message': "Minha dor é insuportável, não aguento mais",
                'min_level': 'high',
                'description': 'Dor emocional extrema'
            },
            {
                'message': "Deletei todos os contatos, não quero mais falar com ninguém",
                'min_level': 'moderate',
                'description': 'Isolamento social extremo'
            }
        ]
        
        print(f"\n📝 Testando {len(subtle_cases)} casos sutis:")
        
        risk_levels = ['low', 'moderate', 'high', 'critical']
        
        improvements = 0
        total_cases = len(subtle_cases)
        
        for i, case in enumerate(subtle_cases, 1):
            result = analyzer.analyze_message(case['message'])
            
            actual_level = result['risk_level']
            min_level = case['min_level']
            
            # Verificar se detectou pelo menos o nível mínimo esperado
            actual_index = risk_levels.index(actual_level)
            min_index = risk_levels.index(min_level)
            
            if actual_index >= min_index:
                print(f"  ✅ Caso {i}: {case['description']}")
                print(f"      '{case['message'][:50]}...' → {actual_level}")
                improvements += 1
            else:
                print(f"  ❌ Caso {i}: {case['description']}")
                print(f"      '{case['message'][:50]}...' → {actual_level} (esperado: ≥{min_level})")
        
        detection_rate = (improvements / total_cases) * 100
        print(f"\n📊 Taxa de detecção melhorada: {detection_rate:.1f}%")
        
        if detection_rate >= 85:
            print("✅ Excelente sensibilidade para casos sutis!")
        elif detection_rate >= 70:
            print("⚠️  Boa sensibilidade, mas pode melhorar")
        else:
            print("❌ Sensibilidade ainda baixa para casos sutis")
        
        return detection_rate >= 85
        
    except Exception as e:
        print(f"❌ Erro no teste sutil: {e}")
        return False

def test_context_modifiers():
    """Testa se modificadores contextuais estão funcionando"""
    print("\n⚡ Testando modificadores contextuais...")
    
    try:
        from app.services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        
        # Casos com e sem modificadores
        test_cases = [
            {
                'base': "Estou triste",
                'modified': "Estou triste e já decidi acabar com tudo hoje",
                'expected_boost': True
            },
            {
                'base': "Penso em desistir",
                'modified': "Penso em desistir e já tenho um plano específico",
                'expected_boost': True
            },
            {
                'base': "Me sinto mal",
                'modified': "Me sinto mal, não é a primeira vez que penso nisso",
                'expected_boost': True
            }
        ]
        
        context_working = 0
        
        for i, case in enumerate(test_cases, 1):
            base_result = analyzer.analyze_message(case['base'])
            modified_result = analyzer.analyze_message(case['modified'])
            
            base_score = base_result['risk_score']
            modified_score = modified_result['risk_score']
            
            has_boost = modified_score > base_score * 1.2  # Pelo menos 20% de aumento
            
            if has_boost == case['expected_boost']:
                print(f"  ✅ Caso {i}: Modificador funcionando")
                print(f"      Base: {base_score:.2f} → Modificado: {modified_score:.2f}")
                context_working += 1
            else:
                print(f"  ❌ Caso {i}: Modificador não detectado")
                print(f"      Base: {base_score:.2f} → Modificado: {modified_score:.2f}")
        
        success_rate = (context_working / len(test_cases)) * 100
        print(f"\n📊 Taxa de sucesso dos modificadores: {success_rate:.1f}%")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ Erro no teste de contexto: {e}")
        return False

def test_emergency_response():
    """Testa resposta de emergência instantânea"""
    print("\n🚑 Testando resposta de emergência...")
    
    try:
        from app.services.risk_analyzer import RiskAnalyzer
        
        analyzer = RiskAnalyzer()
        
        emergency_message = "Quero me matar agora"
        result = analyzer.analyze_message(emergency_message)
        
        # Verificações críticas
        checks = {
            'Nível crítico': result['risk_level'] == 'critical',
            'Score máximo': result['risk_score'] >= 0.9,
            'Alta confiança': result['confidence'] >= 0.9,
            'Tem alerta': 'alert' in result,
            'Recomendações de emergência': len(result['recommendations']) >= 5
        }
        
        print(f"\n🔍 Verificações de emergência:")
        
        passed_checks = 0
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
            if passed:
                passed_checks += 1
        
        # Verificar se tem recomendações urgentes
        urgent_keywords = ['IMEDIATAMENTE', 'AGORA', 'URGENTE', 'CVV', '188']
        recommendations_text = ' '.join(result['recommendations'])
        
        has_urgent = any(keyword in recommendations_text.upper() for keyword in urgent_keywords)
        
        if has_urgent:
            print("  ✅ Recomendações contêm termos urgentes")
            passed_checks += 1
        else:
            print("  ❌ Falta urgência nas recomendações")
        
        total_checks = len(checks) + 1
        emergency_score = (passed_checks / total_checks) * 100
        
        print(f"\n📊 Score de resposta de emergência: {emergency_score:.1f}%")
        
        if emergency_score >= 90:
            print("✅ Resposta de emergência EXCELENTE!")
        elif emergency_score >= 80:
            print("⚠️  Resposta de emergência BOA")
        else:
            print("❌ Resposta de emergência INADEQUADA")
        
        return emergency_score >= 90
        
    except Exception as e:
        print(f"❌ Erro no teste de emergência: {e}")
        return False

def main():
    """Executa todos os testes do sistema melhorado"""
    print("🔥 TESTE DO SISTEMA DE ANÁLISE DE RISCO ULTRA-SENSÍVEL")
    print("="*60)
    
    results = []
    
    # Executar testes
    results.append(("Detecção Crítica Instantânea", test_critical_detection()))
    results.append(("Indicadores Sutis", test_subtle_indicators()))
    results.append(("Modificadores Contextuais", test_context_modifiers()))
    results.append(("Resposta de Emergência", test_emergency_response()))
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("📊 RESUMO - ANÁLISE DE RISCO MELHORADA:")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name:<30} {status}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 Taxa de sucesso geral: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 SISTEMA ULTRA-SENSÍVEL FUNCIONANDO PERFEITAMENTE!")
        print("\n🔥 MELHORIAS IMPLEMENTADAS:")
        print("   ✅ Detecção instantânea de palavras críticas")
        print("   ✅ Análise ultra-sensível de sinais sutis")
        print("   ✅ Modificadores contextuais funcionais")
        print("   ✅ Resposta de emergência imediata")
        print("   ✅ Confiança aumentada nas detecções")
        print("   ✅ Recomendações específicas por situação")
        
        print("\n🎯 AGORA O SISTEMA:")
        print("   • Detecta QUALQUER intenção suicida")
        print("   • Identifica sinais sutis de desesperança")
        print("   • Responde com urgência apropriada")
        print("   • Oferece ajuda específica e imediata")
        
        return True
    else:
        print(f"\n⚠️  Sistema precisa de mais ajustes ({passed_tests}/{total_tests} testes passaram)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
