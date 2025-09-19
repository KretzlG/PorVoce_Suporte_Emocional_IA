"""
Analisador de Risco Profissional para Detecção de Situações Críticas
Sistema especializado em identificar níveis de risco em saúde mental

"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Classe Profissional para Análise de Risco em Saúde Mental
    
    Funcionalidades:
    - Detecção de ideação suicida e autolesão
    - Análise de fatores protetivos
    - Avaliação contextual (urgência, planos específicos)
    - Geração de recomendações personalizadas
    - Análise histórica de risco do usuário
    """
    
    def __init__(self):
        """Inicializa o analisador com padrões e pesos otimizados"""
        
        # === PADRÕES DE RISCO CRÍTICO ===
        # Sistema ULTRA-SENSÍVEL para detecção precoce
        self.critical_patterns = {
            'suicidal_ideation': {
                'patterns': [
                    # Explícitos
                    r'quero morrer',
                    r'vou me matar',
                    r'penso em morrer',
                    r'acabar com tudo',
                    r'por fim na vida',
                    r'suic[ií]dio',
                    r'me jogar da',
                    r'pular da ponte',
                    r'overdose',
                    r'veneno',
                    r'não quero mais viver',
                    r'melhor morto',
                    r'mundo seria melhor sem mim',
                    r'não aguento mais',
                    r'cansei de viver',
                    # Sutis mas críticos
                    r'seria melhor se eu',
                    r'todo mundo ia ficar melhor',
                    r'não faço falta',
                    r'só atrapalho',
                    r'peso para todos',
                    r'desaparecer de vez',
                    r'parar de existir',
                    r'dormir para sempre'
                ],
                'weight': 1.0,  # Peso MÁXIMO
                'level': 'critical'
            },
            'self_harm': {
                'patterns': [
                    r'me cortar',
                    r'me machucar',
                    r'automutilação',
                    r'me queimar',
                    r'bater em mim',
                    r'me ferir',
                    r'arranhar até sangrar',
                    r'cortes no braço',
                    r'me bater',
                    r'dor física para',
                    r'mereço sofrer',
                    r'castigar a mim'
                ],
                'weight': 0.8,  # Alto risco
                'level': 'high'
            },
            'despair_intense': {
                'patterns': [
                    # Desesperança intensa
                    r'sem esperança',
                    r'não tem jeito',
                    r'nunca vai melhorar',
                    r'perdido para sempre',
                    r'sem saída',
                    r'fracassado total',
                    r'inútil completo',
                    r'não serve para nada',
                    r'sem futuro',
                    r'vida acabou',
                    r'não tem volta',
                    r'fim da linha',
                    r'beco sem saída',
                    r'não há solução',
                    # Variações sutis MAS CRÍTICAS
                    r'tudo perdido',
                    r'nada mais importa',
                    r'já era',
                    r'game over',
                    r'não vejo saída',
                    r'não vejo sentido',
                    r'vida sem sentido',
                    r'sem propósito',
                    r'todo mundo melhor',
                    r'saísse de cena',
                    r'simplesmente desaparecesse',
                    r'sentido em nada',
                    r'não tem sentido',
                    r'perdeu o sentido'
                ],
                'weight': 0.8,  # Aumentado para ser mais sensível
                'level': 'critical'  # Mudado para critical
            },
            'emotional_crisis': {
                'patterns': [
                    # Estados emocionais extremos
                    r'desespero total',
                    r'dor insuportável',
                    r'agonia',
                    r'sofrimento extremo',
                    r'não suporto mais',
                    r'limite do limite',
                    r'quebrei',
                    r'destruído',
                    r'despedaçado',
                    r'vazio completo',
                    r'escuridão total',
                    r'abismo',
                    r'buraco negro',
                    r'morto por dentro',
                    r'alma partida'
                ],
                'weight': 0.6,
                'level': 'high'
            },
            'isolation_severe': {
                'patterns': [
                    r'completamente sozinho',
                    r'ninguém me entende',
                    r'todos me abandonaram',
                    r'não tenho ninguém',
                    r'isolado do mundo',
                    r'ninguém se importa',
                    r'invisível para todos',
                    r'esquecido por todos',
                    r'sozinho no mundo',
                    r'ninguém me ama',
                    r'deletei contatos',
                    r'apaguei redes sociais',
                    r'não quero falar com ninguém',
                    r'cortei laços',
                    r'queimei pontes'
                ],
                'weight': 0.5,
                'level': 'moderate'
            },
            'overwhelm_indicators': {
                'patterns': [
                    # Sinais de sobrecarga emocional
                    r'não consigo mais',
                    r'é demais',
                    r'muito pesado',
                    r'não dou conta',
                    r'sobrecarregado',
                    r'esgotado',
                    r'exausto emocionalmente',
                    r'no limite',
                    r'prestes a explodir',
                    r'quebrando por dentro'
                ],
                'weight': 0.4,
                'level': 'moderate'
            },
            'help_seeking': {
                'patterns': [
                    # Pedidos específicos de ajuda (IMPORTANTE detectar)
                    r'preciso de ajuda',
                    r'preciso de suporte',
                    r'podem me ajudar',
                    r'como controlar',
                    r'como lidar com',
                    r'como superar',
                    r'ajuda para',
                    r'tratamento para',
                    r'therapy',
                    r'terapia',
                    r'psicólogo',
                    r'ajuda profissional',
                    r'orientação',
                    r'não sei o que fazer'
                ],
                'weight': 0.2,  # Peso menor - busca de ajuda é positiva
                'level': 'moderate'
            },
            'manageable_conditions': {
                'patterns': [
                    # Condições que a pessoa quer controlar/gerenciar (não críticas)
                    r'controlar minha ansiedade',
                    r'lidar com ansiedade',
                    r'gerenciar estresse',
                    r'melhorar meu humor',
                    r'superar tristeza',
                    r'trabalhar minha autoestima',
                    r'desenvolver habilidades',
                    r'aprender técnicas'
                ],
                'weight': 0.15,  # Peso baixo - são pedidos construtivos
                'level': 'moderate'
            }
        }
        
        # === FATORES PROTETIVOS ===
        # Elementos que reduzem o risco e indicam resiliência
        self.protective_factors = {
            'support_system': [
                r'minha família',
                r'meus amigos',
                r'meu terapeuta',
                r'pessoas que me amam',
                r'não quero magoar',
                r'tenho responsabilidades',
                r'meu parceiro',
                r'minha esposa',
                r'meu marido'
            ],
            'hope_and_gratitude': [
                r'talvez melhore',
                r'vou tentar',
                r'buscar ajuda',
                r'não vou desistir',
                r'força para continuar',
                r'um dia de cada vez',
                r'obrigado',
                r'obrigada',
                r'agradeço',
                r'grato',
                r'grata',
                r'me ajudou',
                r'ajudou muito',
                r'me sinto melhor',
                r'sinto bem',
                r'me sinto bem',
                r'estou bem',
                r'foi útil',
                r'valeu',
                r'muito bom'
            ],
            'treatment': [
                r'tomando medicação',
                r'fazendo terapia',
                r'tratamento',
                r'psicólogo',
                r'psiquiatra',
                r'acompanhamento médico'
            ],
            'positive_state': [
                r'me sinto bem',
                r'estou melhor',
                r'muito obrigado',
                r'obrigado pela conversa',
                r'hoje me sinto bem',
                r'sinto bem hoje',
                r'estou bem hoje',
                r'me sinto melhor hoje',
                r'feliz',
                r'alegre',
                r'animado',
                r'contente',
                r'satisfeito',
                r'aliviado',
                r'esperançoso',
                r'otimista',
                r'confiante',
                r'tranquilo',
                r'calmo'
            ]
        }
        
        # === MODIFICADORES CONTEXTUAIS ULTRA-SENSÍVEIS ===
        # Detecta nuances sutis que aumentam drasticamente o risco
        self.context_modifiers = {
            'urgency_immediate': {
                'patterns': [
                    r'agora', r'hoje', r'esta noite', r'amanhã',
                    r'não aguento mais um dia', r'já decidi',
                    r'dessa vez é sério', r'é a hora'
                ],
                'multiplier': 2.0  # DOBRA o risco
            },
            'specific_plan': {
                'patterns': [
                    r'já escolhi', r'tenho um plano', r'vou fazer',
                    r'já sei como', r'está decidido', r'método',
                    r'preparei tudo', r'só falta'
                ],
                'multiplier': 2.5  # Risco MUITO alto
            },
            'previous_attempts': {
                'patterns': [
                    r'já tentei antes', r'última vez', r'novamente',
                    r'de novo', r'outra vez', r'já fiz isso',
                    r'não é a primeira vez'
                ],
                'multiplier': 1.8
            },
            'finality_language': {
                'patterns': [
                    r'despedida', r'último', r'final', r'tchau para sempre',
                    r'não nos veremos mais', r'é o fim',
                    r'acabou para mim', r'minha última'
                ],
                'multiplier': 2.2
            },
            'substance_involvement': {
                'patterns': [
                    r'bebendo', r'álcool', r'droga', r'remédio',
                    r'pílulas', r'overdose', r'misturar'
                ],
                'multiplier': 1.6
            },
            'social_withdrawal': {
                'patterns': [
                    r'deletei contatos', r'apaguei redes sociais',
                    r'não quero falar com ninguém', r'isolei todos',
                    r'cortei laços', r'queimei pontes'
                ],
                'multiplier': 1.4
            },
            'pain_intensity': {
                'patterns': [
                    r'dói demais', r'insuportável', r'dilacerante',
                    r'tortura', r'agonia', r'martírio',
                    r'inferno', r'cruciante'
                ],
                'multiplier': 1.5
            }
        }
    
    def analyze_message(self, text: str, user_id: int = None) -> Dict:
        """
        ALGORITMO ULTRA-SENSÍVEL para detecção precoce de risco
        Detecta sinais sutis que outros sistemas podem perder
        
        Args:
            text: Texto a ser analisado
            user_id: ID do usuário (para histórico)
            
        Returns:
            Dict com análise completa de risco
        """
        try:
            if not text or not text.strip():
                return self._create_low_risk_result()
            
            text_lower = text.lower().strip()
            
            # === DETECÇÃO INSTANTÂNEA DE PALAVRAS CRÍTICAS ===
            # Qualquer uma dessas palavras = ALERTA IMEDIATO
            instant_critical_words = [
                'suicídio', 'suicidio', 'me matar', 'quero morrer', 
                'acabar com tudo', 'não aguento mais', 'melhor morto',
                'não quero viver', 'não quero mais viver', 'por fim na vida', 
                'desaparecer', 'não quero existir', 'não quero mais existir',
                'cansei de viver', 'mundo melhor sem mim', 'peso para todos',
                'só atrapalho', 'não consigo mais', 'no limite', 'é demais',
                'insuportável', 'muito pesado', 'não dou conta'
            ]
            
            for critical_word in instant_critical_words:
                if critical_word in text_lower:
                    return {
                        'risk_level': 'critical',
                        'risk_score': 1.0,
                        'confidence': 0.95,
                        'factors': [{'category': 'instant_critical', 'trigger': critical_word}],
                        'protective_factors': [],
                        'recommendations': self._generate_emergency_recommendations(),
                        'triggers': [critical_word],
                        'alert': 'RISCO CRÍTICO DETECTADO IMEDIATAMENTE',
                        'analysis_timestamp': datetime.utcnow().isoformat()
                    }
            
            # === ANÁLISE DETALHADA ===
            risk_score = 0.0
            detected_factors = []
            base_confidence = 0.7  # Maior confiança base
            
            # 1. Análise por categoria com SENSIBILIDADE AUMENTADA
            for category, data in self.critical_patterns.items():
                category_score = 0
                category_matches = []
                
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        # Score progressivo - múltiplas correspondências = maior risco
                        category_score += data['weight']
                        category_matches.append(pattern)
                
                if category_matches:
                    detected_factors.append({
                        'category': category,
                        'level': data['level'],
                        'matches': category_matches,
                        'score': category_score,
                        'match_count': len(category_matches)
                    })
                    
                    # Aplicar score com boost para múltiplas correspondências
                    risk_score += category_score * (1 + 0.2 * len(category_matches))
            
            # 1.5. VERIFICAÇÃO ESPECIAL: Pedidos construtivos de ajuda
            constructive_help_patterns = [
                r'preciso de ajuda para controlar',
                r'preciso de ajuda para lidar',
                r'como posso controlar',
                r'como posso lidar',
                r'quero aprender',
                r'gostaria de melhorar'
            ]
            
            is_constructive_help = any(re.search(pattern, text_lower) for pattern in constructive_help_patterns)
            
            if is_constructive_help:
                # Reduzir score para pedidos construtivos
                risk_score = max(0.1, risk_score * 0.5)  # Reduzir pela metade, mínimo 0.1
                detected_factors.append({
                    'category': 'constructive_help_seeking',
                    'level': 'moderate',
                    'matches': ['pedido_construtivo'],
                    'score': 0.1,
                    'match_count': 1
                })
            
            # 1.6. BOOST ADICIONAL para casos que ainda podem estar em zero
            if risk_score == 0:
                # Palavras que indicam risco mas podem não ter sido capturadas
                emergency_indicators = [
                    'deletei contatos', 'apaguei redes', 'isolei todos',
                    'cortei laços', 'queimei pontes', 'não falo com ninguém',
                    'não quero falar', 'não vejo sentido', 'sem sentido',
                    'vida sem sentido', 'não tem sentido', 'sentido em nada'
                ]
                
                for indicator in emergency_indicators:
                    if indicator in text_lower:
                        risk_score += 0.4  # Score base para casos perdidos
                        detected_factors.append({
                            'category': 'missed_risk_indicator',
                            'level': 'moderate',
                            'matches': [indicator],
                            'score': 0.4,
                            'match_count': 1
                        })
                        break
            
            # 2. MODIFICADORES CONTEXTUAIS (CRÍTICOS)
            context_multiplier = 1.0
            context_factors = []
            context_boost = 0.0  # Score adicional por contexto
            
            for modifier, data in self.context_modifiers.items():
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        context_multiplier *= data['multiplier']
                        context_boost += 0.3  # Score base por contexto perigoso
                        context_factors.append({
                            'modifier': modifier,
                            'multiplier': data['multiplier'],
                            'pattern': pattern
                        })
                        break  # Só um por categoria
            
            # Aplicar multiplicador contextual E boost adicional
            if context_factors:
                # Se tinha score, multiplicar
                if risk_score > 0:
                    risk_score *= context_multiplier
                # Sempre adicionar boost contextual
                risk_score += context_boost
            
            # 3. ANÁLISE DE INTENSIDADE EMOCIONAL
            intensity_indicators = [
                r'muito', r'extremamente', r'completamente', r'totalmente',
                r'absurdamente', r'desesperadamente', r'profundamente'
            ]
            
            intensity_count = sum(1 for indicator in intensity_indicators 
                                if re.search(indicator, text_lower))
            
            if intensity_count > 0:
                risk_score += 0.1 * intensity_count  # Boost por intensidade
            
            # 4. VERIFICAR FATORES PROTETIVOS (com peso maior para estados positivos)
            protective_score = 0
            protective_factors_found = []
            
            for category, patterns in self.protective_factors.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        # Dar peso muito maior para estados positivos explícitos
                        if category == 'positive_state':
                            protective_score += 1.0  # Redução máxima para estados positivos
                        elif category == 'hope_and_gratitude':
                            protective_score += 0.6  # Grande redução para gratidão
                        else:
                            protective_score += 0.2  # Redução padrão
                        protective_factors_found.append({
                            'category': category,
                            'pattern': pattern
                        })
            
            # Aplicar redução mais agressiva se houver fatores protetivos
            if protective_score > 0:
                # Se há muitos fatores protetivos, reduzir drasticamente
                if protective_score >= 0.5:
                    risk_score = max(0.0, risk_score - protective_score)  # Pode chegar a zero
                else:
                    risk_score = max(0.1, risk_score - protective_score)  # Redução cautelosa
            
            # 5. DETERMINAÇÃO DE NÍVEL (ULTRA-SENSÍVEL)
            risk_score = min(risk_score, 1.0)
            
            # Limiares MAIS BAIXOS para maior sensibilidade
            if risk_score >= 0.5 or any(f['level'] == 'critical' for f in detected_factors):
                risk_level = 'critical'
                confidence = 0.95
            elif risk_score >= 0.3 or any(f['level'] == 'high' for f in detected_factors):
                risk_level = 'high'
                confidence = 0.9
            elif risk_score >= 0.15 or len(detected_factors) >= 2:
                risk_level = 'moderate'
                confidence = 0.85
            elif risk_score > 0 or len(detected_factors) >= 1:
                risk_level = 'moderate'  # Qualquer detecção = pelo menos moderate
                confidence = 0.8
            else:
                risk_level = 'low'
                confidence = 0.8
            
            # 6. BOOST ADICIONAL para combinações perigosas
            dangerous_combinations = [
                ('despair_intense', 'isolation_severe'),
                ('emotional_crisis', 'substance_involvement'),
                ('suicidal_ideation', 'specific_plan')
            ]
            
            factor_categories = [f['category'] for f in detected_factors]
            for combo in dangerous_combinations:
                if combo[0] in factor_categories and combo[1] in factor_categories:
                    if risk_level != 'critical':
                        risk_level = 'high'
                    risk_score = min(1.0, risk_score + 0.3)
                    confidence = 0.95
            
            # 7. Gerar recomendações específicas
            recommendations = self._generate_recommendations(risk_level, detected_factors)
            
            # 8. Extrair triggers para monitoramento
            triggers = []
            for factor in detected_factors:
                if 'matches' in factor:
                    triggers.extend(factor['matches'])
            
            result = {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'confidence': confidence,
                'factors': detected_factors,
                'context_factors': context_factors,
                'protective_factors': protective_factors_found,
                'recommendations': recommendations,
                'triggers': triggers,
                'intensity_boost': intensity_count,
                'context_multiplier': context_multiplier,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de risco: {e}")
            return self._create_low_risk_result()
    
    def analyze_user_history(self, user_id: int, days: int = 7) -> Dict:
        """
        Analisa histórico de risco de um usuário nos últimos dias
        FUNCIONALIDADE CRÍTICA para identificar padrões e tendências
        
        Args:
            user_id: ID do usuário
            days: Número de dias para análise
            
        Returns:
            Dict com análise histórica e tendências
        """
        try:
            from app.models import RiskAssessment
            from app import db
            
            # Buscar avaliações recentes
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            recent_assessments = RiskAssessment.query.filter(
                RiskAssessment.user_id == user_id,
                RiskAssessment.assessed_at >= cutoff_date
            ).order_by(RiskAssessment.assessed_at.desc()).all()
            
            if not recent_assessments:
                return {
                    'trend': 'no_data',
                    'average_risk': 0.0,
                    'peak_risk': 0.0,
                    'assessment_count': 0
                }
            
            # === ANÁLISE DE TENDÊNCIAS (IMPORTANTE) ===
            risk_scores = [assessment.risk_score for assessment in recent_assessments]
            risk_levels = [assessment.risk_level for assessment in recent_assessments]
            
            # Detectar tendência de piora/melhora
            if len(risk_scores) >= 3:
                recent_avg = sum(risk_scores[:3]) / 3  # Últimas 3 avaliações
                older_avg = sum(risk_scores[-3:]) / 3  # 3 mais antigas
                
                if recent_avg > older_avg + 0.1:
                    trend = 'increasing'  # ALERTA: Risco aumentando
                elif recent_avg < older_avg - 0.1:
                    trend = 'decreasing'  # POSITIVO: Risco diminuindo
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            # Contar episódios críticos
            critical_count = risk_levels.count('critical')
            high_count = risk_levels.count('high')
            
            return {
                'trend': trend,
                'average_risk': sum(risk_scores) / len(risk_scores),
                'peak_risk': max(risk_scores),
                'assessment_count': len(recent_assessments),
                'critical_episodes': critical_count,
                'high_risk_episodes': high_count,
                'latest_assessment': recent_assessments[0].to_dict() if recent_assessments else None
            }
            
        except Exception as e:
            logger.error(f"Erro na análise histórica: {e}")
            return {
                'trend': 'error',
                'average_risk': 0.0,
                'peak_risk': 0.0,
                'assessment_count': 0
            }
    
    def _generate_recommendations(self, risk_level: str, factors: List[Dict]) -> List[str]:
        """
        Gera recomendações personalizadas baseadas no nível de risco
        FUNÇÃO CRÍTICA para orientar ações apropriadas
        
        Args:
            risk_level: Nível de risco detectado
            factors: Fatores de risco identificados
            
        Returns:
            Lista de recomendações prioritizadas
        """
        recommendations = []
        
        # === RECOMENDAÇÕES POR NÍVEL DE RISCO (TRIAGEM INTERNA) ===
        
        if risk_level == 'critical':
            recommendations = [
                "🚨 SITUAÇÃO CRÍTICA DETECTADA",
                "� ENCAMINHANDO PARA TRIAGEM ESPECIALIZADA IMEDIATA",
                "👨‍⚕️ Nossa equipe de profissionais irá entrar em contato",
                "👥 Entre em contato com alguém de confiança AGORA",
                "🛡️ Remova objetos que possam causar autolesão",
                "❌ NÃO fique sozinho(a) - busque companhia imediata"
            ]
        
        elif risk_level == 'high':
            recommendations = [
                "⚠️ TRIAGEM URGENTE NECESSÁRIA",
                "� Conectando com nossa equipe especializada",
                "�‍⚕️ Um profissional irá avaliar seu caso prioritariamente",
                "👨‍👩‍👧‍👦 Peça apoio de familiares ou amigos próximos",
                "🛡️ Mantenha-se em ambiente seguro",
                "⏰ Evite ficar sozinho(a) por períodos longos"
            ]
        
        elif risk_level == 'moderate':
            recommendations = [
                "💭 TRIAGEM RECOMENDADA para melhor suporte",
                "🗣️ Nossa equipe pode te ajudar com estratégias personalizadas",
                "🧘 Pratique técnicas de relaxamento enquanto organizamos o atendimento",
                "📅 Mantenha uma rotina saudável",
                "� Converse com alguém de confiança",
                "🤝 Evite isolamento social"
            ]
        
        else:  # low
            recommendations = [
                "💚 Continue cuidando da sua saúde mental",
                "👥 Mantenha contato com pessoas queridas",
                "🎯 Pratique atividades que te fazem bem",
                "🔄 Lembre-se: é normal ter altos e baixos",
                "🤝 Nossa plataforma está sempre aqui para apoiá-lo"
            ]
        
        # === RECOMENDAÇÕES ESPECÍFICAS POR FATORES ===
        factor_categories = [f['category'] for f in factors if 'category' in f]
        
        if 'isolation' in factor_categories:
            recommendations.append("🌐 Nossa equipe pode ajudar você a se reconectar")
        
        if 'anxiety_panic' in factor_categories:
            recommendations.append("🫁 Pratique respiração profunda (4-7-8) - técnica que ensinaremos")
        
        if 'severe_depression' in factor_categories:
            recommendations.append("💊 Nossa triagem avaliará necessidade de suporte médico")
        
        return recommendations
    
    def _generate_emergency_recommendations(self) -> List[str]:
        """
        Gera recomendações IMEDIATAS para situações críticas detectadas instantaneamente
        """
        return [
            "🚨 SITUAÇÃO CRÍTICA - TRIAGEM EMERGENCIAL ATIVADA",
            "� NOSSA EQUIPE ESPECIALIZADA FOI NOTIFICADA",
            "👨‍⚕️ UM PROFISSIONAL ENTRARÁ EM CONTATO IMEDIATAMENTE",
            "👨‍👩‍👧‍👦 CHAME FAMILIAR/AMIGO PARA FICAR COM VOCÊ",
            "🛡️ REMOVA QUALQUER MEIO DE AUTOLESÃO DO ALCANCE",
            "⏰ AGUARDE NOSSO CONTATO - VOCÊ NÃO ESTÁ SOZINHO",
            "💙 SUA VIDA TEM VALOR - NOSSA EQUIPE ESTÁ AQUI PARA AJUDAR"
        ]
    
    def _create_low_risk_result(self) -> Dict:
        """Cria resultado padrão para baixo risco"""
        return {
            'risk_level': 'low',
            'risk_score': 0.0,
            'confidence': 0.5,
            'factors': [],
            'protective_factors': [],
            'recommendations': [
                "💚 Continue cuidando da sua saúde mental",
                "🔄 Lembre-se: é normal ter altos e baixos"
            ],
            'triggers': [],
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def get_emergency_contacts(self) -> List[Dict]:
        """
        Retorna lista de contatos internos de triagem e suporte
        INFORMAÇÃO CRÍTICA para situações de risco
        """
        return [
            {
                'name': 'Triagem Especializada Interna',
                'phone': 'sistema_interno',
                'description': 'Equipe de profissionais especializados em saúde mental - 24h',
                'type': 'internal_triage',
                'priority': 1
            },
            {
                'name': 'Suporte Emergencial',
                'phone': 'plataforma_interna',
                'description': 'Canal direto para situações críticas',
                'type': 'emergency_support',
                'priority': 2
            },
            {
                'name': 'Acompanhamento Psicológico',
                'phone': 'agendamento_interno',
                'description': 'Sessões com psicólogos da plataforma',
                'type': 'psychological_support',
                'priority': 3
            },
            {
                'name': 'Monitoramento 24h',
                'phone': 'sistema_automatico',
                'description': 'Acompanhamento contínuo via IA e profissionais',
                'type': 'continuous_monitoring',
                'priority': 4
            }
        ]
