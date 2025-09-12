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
        # Organizados por categoria para melhor manutenção
        self.critical_patterns = {
            'suicidal_ideation': {
                'patterns': [
                    r'(quero|vou|pretendo|penso em|tento|tentei|iria|gostaria de) morrer',
                    r'(quero|vou|pretendo|penso em|tento|tentei|iria|gostaria de) me matar',
                    r'acabar com tudo',
                    r'por fim na vida',
                    r'suic[ií]dio',
                    r'me jogar da',
                    r'pular da ponte',
                    r'overdose',
                    r'veneno',
                    r'não aguento mais viver',
                    r'melhor morto',
                    r'mundo seria melhor sem mim'
                ],
                'weight': 0.9,  # Peso máximo para padrões críticos
                'level': 'critical'
            },
            'self_harm': {
                'patterns': [
                    r'me cortar',
                    r'me machucar',
                    r'automutilação',
                    r'me queimar',
                    r'bater em mim mesmo',
                    r'me ferir',
                    r'arranhar até sangrar',
                    r'cortes no braço'
                ],
                'weight': 0.7,
                'level': 'high'
            },
            'hopelessness': {
                'patterns': [
                    r'sem esperança',
                    r'não tem jeito',
                    r'nunca vai melhorar',
                    r'perdido para sempre',
                    r'sem saída',
                    r'fracassado',
                    r'inútil',
                    r'não serve para nada',
                    r'sem futuro'
                ],
                'weight': 0.6,
                'level': 'high'
            },
            'severe_depression': {
                'patterns': [
                    r'depressão profunda',
                    r'vazio total',
                    r'escuridão completa',
                    r'não sinto nada',
                    r'morto por dentro',
                    r'sem energia para nada',
                    r'não consigo sair da cama',
                    r'perdeu o sentido'
                ],
                'weight': 0.5,
                'level': 'moderate'
            },
            'isolation': {
                'patterns': [
                    r'completamente sozinho',
                    r'ninguém me entende',
                    r'todos me abandonaram',
                    r'não tenho ninguém',
                    r'isolado do mundo',
                    r'ninguém se importa'
                ],
                'weight': 0.4,
                'level': 'moderate'
            },
            'anxiety_panic': {
                'patterns': [
                    r'ataque de pânico',
                    r'não consigo respirar',
                    r'coração disparado',
                    r'medo extremo',
                    r'terror constante',
                    r'ansiedade paralisante'
                ],
                'weight': 0.3,
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
                r'tenho responsabilidades'
            ],
            'hope': [
                r'talvez melhore',
                r'vou tentar',
                r'buscar ajuda',
                r'não vou desistir',
                r'força para continuar',
                r'um dia de cada vez'
            ],
            'treatment': [
                r'tomando medicação',
                r'fazendo terapia',
                r'tratamento',
                r'psicólogo',
                r'psiquiatra',
                r'acompanhamento médico'
            ]
        }
        
        # === MODIFICADORES CONTEXTUAIS ===
        # Fatores que aumentam a urgência e gravidade
        self.context_modifiers = {
            'time_urgency': {
                'patterns': [r'agora', r'hoje', r'esta noite', r'amanhã'],
                'multiplier': 1.3  # Aumenta risco em 30%
            },
            'specific_plan': {
                'patterns': [r'já escolhi', r'tenho um plano', r'vou fazer'],
                'multiplier': 1.5  # Aumenta risco em 50%
            },
            'previous_attempts': {
                'patterns': [r'já tentei antes', r'última vez', r'novamente'],
                'multiplier': 1.2  # Aumenta risco em 20%
            }
        }
    
    def analyze_message(self, text: str, user_id: int = None) -> Dict:
        """
        Método principal: analisa uma mensagem e retorna avaliação completa de risco
        
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
            
            # === ANÁLISE PRINCIPAL ===
            risk_score = 0.0
            detected_factors = []
            risk_level = 'low'
            confidence = 0.5
            
            # 1. Analisar padrões de risco por categoria
            for category, data in self.critical_patterns.items():
                category_score = 0
                category_matches = []
                
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        category_score += data['weight']
                        category_matches.append(pattern)
                
                if category_matches:
                    detected_factors.append({
                        'category': category,
                        'level': data['level'],
                        'matches': category_matches,
                        'score': category_score
                    })
                    risk_score += category_score
            
            # 2. Aplicar modificadores contextuais (IMPORTANTE)
            for modifier, data in self.context_modifiers.items():
                for pattern in data['patterns']:
                    if re.search(pattern, text_lower):
                        risk_score *= data['multiplier']
                        detected_factors.append({
                            'category': f'context_{modifier}',
                            'level': 'modifier',
                            'multiplier': data['multiplier']
                        })
                        break
            
            # 3. Verificar fatores protetivos (REDUZEM O RISCO)
            protective_score = 0
            protective_factors = []
            
            for category, patterns in self.protective_factors.items():
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        protective_score += 0.2
                        protective_factors.append({
                            'category': category,
                            'pattern': pattern
                        })
            
            # Aplicar redução por fatores protetivos
            if protective_score > 0:
                risk_score = max(0, risk_score - protective_score)
            
            # 4. Normalizar score e determinar nível
            risk_score = min(risk_score, 1.0)
            
            if risk_score >= 0.8:
                risk_level = 'critical'
                confidence = 0.9
            elif risk_score >= 0.6:
                risk_level = 'high'
                confidence = 0.85
            elif risk_score >= 0.3:
                risk_level = 'moderate'
                confidence = 0.75
            else:
                risk_level = 'low'
                confidence = 0.7
            
            # 5. Gerar recomendações personalizadas
            recommendations = self._generate_recommendations(risk_level, detected_factors)
            
            # 6. Extrair triggers específicos
            triggers = [factor['matches'] for factor in detected_factors 
                       if 'matches' in factor]
            triggers = [item for sublist in triggers for item in sublist]  # Flatten
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'confidence': confidence,
                'factors': detected_factors,
                'protective_factors': protective_factors,
                'recommendations': recommendations,
                'triggers': triggers,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
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
        
        # === RECOMENDAÇÕES POR NÍVEL DE RISCO ===
        
        if risk_level == 'critical':
            recommendations = [
                "🚨 PROCURE AJUDA PROFISSIONAL IMEDIATAMENTE",
                "📞 Ligue para o CVV: 188 (24 horas)",
                "🏥 Vá ao hospital ou pronto-socorro mais próximo",
                "👥 Entre em contato com alguém de confiança AGORA",
                "🛡️ Remova objetos que possam causar autolesão",
                "❌ NÃO fique sozinho(a)"
            ]
        
        elif risk_level == 'high':
            recommendations = [
                "⚠️ Busque ajuda profissional urgentemente",
                "👨‍⚕️ Converse com um psicólogo ou psiquiatra hoje",
                "📞 Ligue para o CVV: 188 se precisar conversar",
                "👨‍👩‍👧‍👦 Peça apoio de familiares ou amigos próximos",
                "🏥 Considere internação voluntária se necessário",
                "⏰ Evite ficar sozinho(a) por períodos longos"
            ]
        
        elif risk_level == 'moderate':
            recommendations = [
                "💭 Considere buscar apoio profissional",
                "🗣️ Converse com alguém de confiança",
                "🧘 Pratique técnicas de relaxamento",
                "📅 Mantenha uma rotina saudável",
                "📞 CVV disponível 24h no 188",
                "🤝 Evite isolamento social"
            ]
        
        else:  # low
            recommendations = [
                "💚 Continue cuidando da sua saúde mental",
                "👥 Mantenha contato com pessoas queridas",
                "🎯 Pratique atividades que te fazem bem",
                "🔄 Lembre-se: é normal ter altos e baixos",
                "📞 CVV sempre disponível: 188"
            ]
        
        # === RECOMENDAÇÕES ESPECÍFICAS POR FATORES ===
        factor_categories = [f['category'] for f in factors if 'category' in f]
        
        if 'isolation' in factor_categories:
            recommendations.append("🌐 Procure reconectar-se com pessoas importantes")
        
        if 'anxiety_panic' in factor_categories:
            recommendations.append("🫁 Pratique respiração profunda (4-7-8)")
        
        if 'severe_depression' in factor_categories:
            recommendations.append("💊 Considere medicação antidepressiva com acompanhamento médico")
        
        return recommendations
    
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
        Retorna lista completa de contatos de emergência
        INFORMAÇÃO CRÍTICA para situações de risco
        """
        return [
            {
                'name': 'CVV - Centro de Valorização da Vida',
                'phone': '188',
                'description': 'Apoio emocional e prevenção ao suicídio - 24h',
                'type': 'emotional_support',
                'priority': 1
            },
            {
                'name': 'SAMU',
                'phone': '192',
                'description': 'Emergências médicas',
                'type': 'medical_emergency',
                'priority': 2
            },
            {
                'name': 'Polícia Militar',
                'phone': '190',
                'description': 'Emergências policiais',
                'type': 'security',
                'priority': 3
            },
            {
                'name': 'Bombeiros',
                'phone': '193',
                'description': 'Emergências e resgates',
                'type': 'rescue',
                'priority': 4
            }
        ]
