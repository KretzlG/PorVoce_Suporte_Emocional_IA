"""
Sistema de Prompt Engineering Avançado para Suporte Emocional
Integra contexto de treinamento, conversas e estratégias específicas
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PromptType(Enum):
    """Tipos de prompt disponíveis"""
    EMPATHETIC_RESPONSE = "empathetic_response"
    CRISIS_INTERVENTION = "crisis_intervention"
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MOTIVATIONAL = "motivational"
    MINDFULNESS_BASED = "mindfulness_based"
    SOLUTION_FOCUSED = "solution_focused"
    PSYCHOEDUCATIONAL = "psychoeducational"


class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PromptContext:
    """Contexto para construção de prompts"""
    user_message: str
    risk_level: RiskLevel
    user_name: Optional[str] = None
    session_history: Optional[List[Dict]] = None
    training_context: Optional[str] = None
    conversation_examples: Optional[List[Dict]] = None
    emotional_state: Optional[str] = None
    dominant_themes: Optional[List[str]] = None
    therapeutic_approach: Optional[PromptType] = None


class AdvancedPromptEngineer:
    """
    Sistema Avançado de Prompt Engineering para Suporte Emocional
    
    Funcionalidades:
    - Prompts adaptativos baseados no contexto
    - Integração com dados de treinamento
    - Estratégias terapêuticas específicas
    - Personalização por nível de risco
    - Templates modulares e extensíveis
    """
    
    def __init__(self):
        self.prompt_templates = self._initialize_templates()
        self.therapeutic_strategies = self._initialize_therapeutic_strategies()
        self.risk_adaptations = self._initialize_risk_adaptations()
        logger.info("AdvancedPromptEngineer inicializado")
    
    def build_contextual_prompt(self, context: PromptContext, 
                              provider: str = 'openai') -> Dict:
        """
        Constrói prompt contextualizado baseado no contexto fornecido
        
        Args:
            context: Contexto completo para construção
            provider: Provedor de IA ('openai', 'gemini', etc.)
            
        Returns:
            Dict com prompt estruturado e configurações
        """
        try:
            # 1. Determinar estratégia terapêutica
            therapeutic_approach = self._determine_therapeutic_approach(context)
            
            # 2. Construir seções do prompt
            prompt_sections = self._build_prompt_sections(context, therapeutic_approach)
            
            # 3. Integrar dados de treinamento se disponível
            if context.training_context:
                prompt_sections['training_integration'] = self._integrate_training_data(
                    context.training_context, context.risk_level
                )
            
            # 4. Adicionar exemplos de conversas se disponível
            if context.conversation_examples:
                prompt_sections['conversation_examples'] = self._format_conversation_examples(
                    context.conversation_examples, context.risk_level
                )
            
            # 5. Construir prompt final baseado no provedor
            if provider == 'openai':
                return self._build_openai_prompt(prompt_sections, context)
            elif provider == 'gemini':
                return self._build_gemini_prompt(prompt_sections, context)
            else:
                return self._build_generic_prompt(prompt_sections, context)
                
        except Exception as e:
            logger.error(f"Erro na construção do prompt: {e}")
            return self._build_fallback_prompt(context, provider)
    
    def _initialize_templates(self) -> Dict:
        """Inicializa templates base de prompts"""
        return {
            'system_base': """Você é um assistente especializado em suporte emocional e bem-estar mental. 
Suas respostas devem ser:
- Empáticas e compreensivas
- Baseadas em evidências científicas
- Práticas e aplicáveis
- Respeitosas e não-julgamentais
- Orientadas para soluções quando apropriado

IMPORTANTE: Sempre priorize a segurança. Em casos de risco alto, encoraje busca por ajuda profissional.""",

            'risk_critical': """⚠️ PROTOCOLO DE CRISE ATIVADO ⚠️
Esta pessoa pode estar em risco imediato. Sua resposta deve:
1. Validar os sentimentos sem minimizar
2. Oferecer recursos de emergência imediatos
3. Encorajar contato com profissionais
4. Demonstrar que a vida tem valor
5. Sugerir estratégias de segurança imediata

RECURSOS DE EMERGÊNCIA:
- CVV: 188 (24h, gratuito)
- SAMU: 192
- Bombeiros: 193""",

            'empathetic_foundation': """Responda com profunda empatia, reconhecendo que:
- Os sentimentos da pessoa são válidos e compreensíveis
- Cada experiência é única e significativa
- Não há julgamento, apenas acolhimento
- O sofrimento merece ser ouvido e compreendido""",

            'solution_focused': """Mantenha foco nas soluções e recursos, explorando:
- Forças e recursos internos da pessoa
- Momentos de exceção (quando o problema não estava presente)
- Pequenos passos práticos e alcançáveis
- Objetivos claros e mensuráveis""",

            'cognitive_behavioral': """Aplique princípios da Terapia Cognitivo-Comportamental:
- Identifique padrões de pensamento
- Questione pensamentos automáticos negativos
- Conecte pensamentos, sentimentos e comportamentos
- Sugira experimentos comportamentais pequenos""",

            'mindfulness_integration': """Integre elementos de mindfulness:
- Atenção ao momento presente
- Aceitação sem julgamento
- Técnicas de respiração e grounding
- Observação dos pensamentos sem identificação total"""
        }
    
    def _initialize_therapeutic_strategies(self) -> Dict:
        """Inicializa estratégias terapêuticas específicas"""
        return {
            PromptType.EMPATHETIC_RESPONSE: {
                'focus': 'validação e acolhimento emocional',
                'techniques': ['escuta ativa', 'reflexo de sentimentos', 'normalização'],
                'phrases': [
                    "Entendo que você está passando por um momento muito difícil",
                    "Seus sentimentos são completamente compreensíveis nesta situação",
                    "Não está sozinho(a) neste processo"
                ]
            },
            
            PromptType.CRISIS_INTERVENTION: {
                'focus': 'segurança imediata e estabilização',
                'techniques': ['avaliação de risco', 'plano de segurança', 'recursos de emergência'],
                'phrases': [
                    "Sua vida tem valor e importância",
                    "Existem pessoas que podem ajudar agora mesmo",
                    "Este momento difícil pode passar"
                ]
            },
            
            PromptType.COGNITIVE_BEHAVIORAL: {
                'focus': 'identificação e modificação de padrões de pensamento',
                'techniques': ['reestruturação cognitiva', 'experimentos comportamentais', 'automonitoramento'],
                'phrases': [
                    "Vamos examinar este pensamento mais de perto",
                    "Que evidências apoiam ou contradizem esta ideia?",
                    "Como você poderia testar se isso é realmente verdade?"
                ]
            },
            
            PromptType.MINDFULNESS_BASED: {
                'focus': 'consciência presente e aceitação',
                'techniques': ['respiração consciente', 'body scan', 'observação sem julgamento'],
                'phrases': [
                    "Vamos focar no que você pode sentir neste momento",
                    "Notice estes pensamentos como nuvens passando no céu",
                    "Respire profundamente e volte ao momento presente"
                ]
            },
            
            PromptType.SOLUTION_FOCUSED: {
                'focus': 'recursos internos e soluções práticas',
                'techniques': ['escala de bem-estar', 'perguntas do milagre', 'exceções'],
                'phrases': [
                    "Quando você já lidou bem com algo similar?",
                    "Que recursos internos você tem para enfrentar isso?",
                    "Qual seria um pequeno primeiro passo?"
                ]
            }
        }
    
    def _initialize_risk_adaptations(self) -> Dict:
        """Inicializa adaptações específicas por nível de risco"""
        return {
            RiskLevel.LOW: {
                'tone': 'encorajador e exploratório',
                'focus': 'crescimento e desenvolvimento',
                'suggestions': ['autoconhecimento', 'metas pessoais', 'bem-estar preventivo']
            },
            
            RiskLevel.MODERATE: {
                'tone': 'solidário e prático',
                'focus': 'estratégias de enfrentamento',
                'suggestions': ['técnicas de manejo', 'suporte social', 'atividades regulares']
            },
            
            RiskLevel.HIGH: {
                'tone': 'cuidadoso e direcionado',
                'focus': 'estabilização e suporte',
                'suggestions': ['ajuda profissional', 'rede de apoio', 'cuidados imediatos']
            },
            
            RiskLevel.CRITICAL: {
                'tone': 'urgente mas acolhedor',
                'focus': 'segurança imediata',
                'suggestions': ['emergência médica', 'acompanhamento constante', 'hospitalização se necessário']
            }
        }
    
    def _determine_therapeutic_approach(self, context: PromptContext) -> PromptType:
        """Determina a melhor abordagem terapêutica baseada no contexto"""
        
        # Casos críticos sempre usam intervenção de crise
        if context.risk_level == RiskLevel.CRITICAL:
            return PromptType.CRISIS_INTERVENTION
        
        # Se há abordagem específica solicitada
        if context.therapeutic_approach:
            return context.therapeutic_approach
        
        # Baseado no conteúdo da mensagem
        message_lower = context.user_message.lower()
        
        # Indicadores para diferentes abordagens
        cognitive_indicators = ['penso que', 'acredito que', 'tenho certeza', 'sempre acontece', 'nunca consigo']
        mindfulness_indicators = ['ansioso', 'acelerado', 'mente correndo', 'não paro de pensar']
        solution_indicators = ['o que fazer', 'como resolver', 'preciso de ajuda para', 'não sei como']
        
        # Contar indicadores
        cognitive_score = sum(1 for indicator in cognitive_indicators if indicator in message_lower)
        mindfulness_score = sum(1 for indicator in mindfulness_indicators if indicator in message_lower)
        solution_score = sum(1 for indicator in solution_indicators if indicator in message_lower)
        
        # Determinar abordagem
        if solution_score >= 2:
            return PromptType.SOLUTION_FOCUSED
        elif cognitive_score >= 2:
            return PromptType.COGNITIVE_BEHAVIORAL
        elif mindfulness_score >= 2:
            return PromptType.MINDFULNESS_BASED
        elif context.risk_level == RiskLevel.HIGH:
            return PromptType.CRISIS_INTERVENTION
        else:
            return PromptType.EMPATHETIC_RESPONSE
    
    def _build_prompt_sections(self, context: PromptContext, 
                              therapeutic_approach: PromptType) -> Dict:
        """Constrói seções específicas do prompt"""
        
        sections = {}
        
        # 1. Sistema base
        sections['system_base'] = self.prompt_templates['system_base']
        
        # 2. Adaptação por risco
        risk_adaptation = self.risk_adaptations[context.risk_level]
        sections['risk_adaptation'] = f"""
NÍVEL DE RISCO: {context.risk_level.value.upper()}
Tom da resposta: {risk_adaptation['tone']}
Foco principal: {risk_adaptation['focus']}
Sugestões prioritárias: {', '.join(risk_adaptation['suggestions'])}
"""
        
        # 3. Estratégia terapêutica
        strategy = self.therapeutic_strategies[therapeutic_approach]
        sections['therapeutic_strategy'] = f"""
ABORDAGEM TERAPÊUTICA: {therapeutic_approach.value}
Foco: {strategy['focus']}
Técnicas: {', '.join(strategy['techniques'])}

Frases úteis para incorporar:
{chr(10).join(['- ' + phrase for phrase in strategy['phrases']])}
"""
        
        # 4. Protocolo específico para risco crítico
        if context.risk_level == RiskLevel.CRITICAL:
            sections['crisis_protocol'] = self.prompt_templates['risk_critical']
        
        # 5. Contexto do usuário
        if context.user_name:
            sections['user_context'] = f"Nome do usuário: {context.user_name}"
        
        # 6. Estado emocional se conhecido
        if context.emotional_state:
            sections['emotional_context'] = f"Estado emocional identificado: {context.emotional_state}"
        
        # 7. Temas dominantes se identificados
        if context.dominant_themes:
            sections['themes_context'] = f"Temas principais: {', '.join(context.dominant_themes)}"
        
        return sections
    
    def _integrate_training_data(self, training_context: str, risk_level: RiskLevel) -> str:
        """Integra dados de treinamento ao prompt"""
        
        integration = f"""
=== CONHECIMENTO ESPECIALIZADO RELEVANTE ===
{training_context}

INSTRUÇÕES PARA USO:
- Use este conhecimento como base científica para sua resposta
- Adapte as informações para o contexto específico do usuário
- Mantenha linguagem acessível e não técnica
- Priorize aspectos mais relevantes para o nível de risco {risk_level.value}
"""
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            integration += "\n- FOQUE em informações sobre segurança e recursos de emergência"
        
        return integration
    
    def _format_conversation_examples(self, conversation_examples: List[Dict], 
                                    risk_level: RiskLevel) -> str:
        """Formata exemplos de conversas bem-sucedidas"""
        
        if not conversation_examples:
            return ""
        
        formatted = "=== EXEMPLOS DE RESPOSTAS EFICAZES ===\\n"
        
        for i, example in enumerate(conversation_examples[:2], 1):  # Máximo 2 exemplos
            rating = "⭐" * int(example.get('rating', 3))
            formatted += f"""
💬 Exemplo {i} ({rating}):
Situação: {example.get('user_message', '')}
Resposta eficaz: {example.get('ai_response', '')}
Por que funcionou: Abordagem {example.get('risk_level', 'adequada')} para o contexto
"""
        
        formatted += """
COMO USAR ESTES EXEMPLOS:
- Inspire-se no tom e abordagem, mas personalize para o caso atual
- Note como as respostas eficazes equilibram empatia com orientação prática
- Adapte o nível de intervenção para o risco identificado
"""
        
        return formatted
    
    def _build_openai_prompt(self, sections: Dict, context: PromptContext) -> Dict:
        """Constrói prompt específico para OpenAI"""
        
        # Mensagem do sistema
        system_parts = [sections['system_base']]
        
        if 'crisis_protocol' in sections:
            system_parts.append(sections['crisis_protocol'])
        
        system_parts.append(sections['risk_adaptation'])
        system_parts.append(sections['therapeutic_strategy'])
        
        if 'training_integration' in sections:
            system_parts.append(sections['training_integration'])
        
        if 'conversation_examples' in sections:
            system_parts.append(sections['conversation_examples'])
        
        # Instruções finais
        system_parts.append("""
INSTRUÇÕES FINAIS:
1. Responda de forma calorosa e humana
2. Use no máximo 200-300 palavras
3. Ofereça pelo menos uma sugestão prática
4. Termine com uma pergunta aberta ou convite para continuar a conversa
5. Se risco alto/crítico, SEMPRE mencione recursos profissionais
""")
        
        # Contexto adicional do usuário
        if any(k in sections for k in ['user_context', 'emotional_context', 'themes_context']):
            context_info = []
            for key in ['user_context', 'emotional_context', 'themes_context']:
                if key in sections:
                    context_info.append(sections[key])
            system_parts.append("CONTEXTO DO USUÁRIO:\\n" + "\\n".join(context_info))
        
        # Mensagens
        messages = [
            {"role": "system", "content": "\\n\\n".join(system_parts)},
            {"role": "user", "content": context.user_message}
        ]
        
        # Histórico da conversa se disponível
        if context.session_history:
            # Inserir histórico antes da mensagem atual
            history_messages = []
            for msg in context.session_history[-6:]:  # Últimas 6 mensagens
                if msg.get('role') in ['user', 'assistant']:
                    history_messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            messages = [messages[0]] + history_messages + [messages[1]]
        
        return {
            'messages': messages,
            'max_tokens': 400 if context.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else 300,
            'temperature': 0.7,
            'presence_penalty': 0.1,
            'frequency_penalty': 0.1
        }
    
    def _build_gemini_prompt(self, sections: Dict, context: PromptContext) -> Dict:
        """Constrói prompt específico para Gemini"""
        
        prompt_parts = []
        
        # Sistema e instruções principais
        prompt_parts.append(sections['system_base'])
        prompt_parts.append(sections['risk_adaptation'])
        prompt_parts.append(sections['therapeutic_strategy'])
        
        # Protocolo de crise se necessário
        if 'crisis_protocol' in sections:
            prompt_parts.append(sections['crisis_protocol'])
        
        # Dados de treinamento
        if 'training_integration' in sections:
            prompt_parts.append(sections['training_integration'])
        
        # Exemplos de conversas
        if 'conversation_examples' in sections:
            prompt_parts.append(sections['conversation_examples'])
        
        # Contexto do usuário
        if any(k in sections for k in ['user_context', 'emotional_context', 'themes_context']):
            context_info = []
            for key in ['user_context', 'emotional_context', 'themes_context']:
                if key in sections:
                    context_info.append(sections[key])
            prompt_parts.append("CONTEXTO DO USUÁRIO:\\n" + "\\n".join(context_info))
        
        # Mensagem do usuário
        prompt_parts.append(f"\\nMENSAGEM DO USUÁRIO:\\n{context.user_message}")
        
        # Instruções de resposta
        prompt_parts.append("""
RESPONDA AGORA:
- Com empatia e compreensão
- De forma prática e útil
- Respeitando o nível de risco identificado
- Em português brasileiro
- Com no máximo 250 palavras
""")
        
        return {
            'prompt': "\\n\\n".join(prompt_parts),
            'max_tokens': 350,
            'temperature': 0.7
        }
    
    def _build_generic_prompt(self, sections: Dict, context: PromptContext) -> Dict:
        """Constrói prompt genérico para outros provedores"""
        return self._build_gemini_prompt(sections, context)
    
    def _build_fallback_prompt(self, context: PromptContext, provider: str) -> Dict:
        """Constrói prompt de fallback em caso de erro"""
        
        fallback_system = f"""Você é um assistente de suporte emocional. 
Responda com empatia para esta situação de nível de risco {context.risk_level.value}.
Seja compreensivo, prático e ofereça apoio genuíno."""
        
        if provider == 'openai':
            return {
                'messages': [
                    {"role": "system", "content": fallback_system},
                    {"role": "user", "content": context.user_message}
                ],
                'max_tokens': 250,
                'temperature': 0.7
            }
        else:
            return {
                'prompt': f"{fallback_system}\\n\\nUsuário: {context.user_message}\\n\\nResposta:",
                'max_tokens': 250,
                'temperature': 0.7
            }
    
    def get_prompt_statistics(self) -> Dict:
        """Retorna estatísticas sobre uso de prompts"""
        return {
            'available_prompt_types': [pt.value for pt in PromptType],
            'risk_levels': [rl.value for rl in RiskLevel],
            'templates_count': len(self.prompt_templates),
            'strategies_count': len(self.therapeutic_strategies),
            'risk_adaptations_count': len(self.risk_adaptations)
        }
    
    def validate_prompt_context(self, context: PromptContext) -> Tuple[bool, List[str]]:
        """Valida se o contexto do prompt está completo"""
        
        errors = []
        
        if not context.user_message or not context.user_message.strip():
            errors.append("Mensagem do usuário não pode estar vazia")
        
        if not isinstance(context.risk_level, RiskLevel):
            errors.append("Nível de risco deve ser um RiskLevel válido")
        
        if context.session_history and not isinstance(context.session_history, list):
            errors.append("Histórico da sessão deve ser uma lista")
        
        if context.dominant_themes and not isinstance(context.dominant_themes, list):
            errors.append("Temas dominantes devem ser uma lista")
        
        return len(errors) == 0, errors


# Instância global para uso fácil
advanced_prompt_engineer = AdvancedPromptEngineer()