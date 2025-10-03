# --- Regra de transição de risco ---
def validate_risk_transition(previous: "RiskLevel", new: "RiskLevel") -> "RiskLevel":
    """
    Garante que não haja descida abrupta de 'critical' para 'low'.
    Se anterior era 'critical', só permite 'critical' ou 'high'.
    Caso contrário, retorna o anterior.
    """
    if previous == RiskLevel.CRITICAL and new in [RiskLevel.LOW, RiskLevel.MODERATE]:
        # Mantém 'critical' ou permite apenas 'high'
        return RiskLevel.HIGH if new == RiskLevel.HIGH else RiskLevel.CRITICAL
    return new

# Sistema de Prompts para IA de Suporte Emocional
# Centraliza templates, instruções e configurações de tom
# Refatorado para facilitar manutenção e extensão

import logging
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PromptType(Enum):
    EMPATHETIC_RESPONSE = "empathetic_response"
    CRISIS_INTERVENTION = "crisis_intervention"
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"
    MINDFULNESS_BASED = "mindfulness_based"
    SOLUTION_FOCUSED = "solution_focused"



class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

# --- Regra de transição de risco ---
def validate_risk_transition(previous: RiskLevel, new: RiskLevel) -> RiskLevel:
    """
    Garante que não haja descida abrupta de 'critical' para 'low'.
    Se anterior era 'critical', só permite 'critical' ou 'high'.
    Caso contrário, retorna o anterior.
    """
    if previous == RiskLevel.CRITICAL and new in [RiskLevel.LOW, RiskLevel.MODERATE]:
        # Mantém 'critical' ou permite apenas 'high'
        return RiskLevel.HIGH if new == RiskLevel.HIGH else RiskLevel.CRITICAL
    return new


@dataclass
class PromptContext:
    user_message: str
    risk_level: RiskLevel
    user_name: Optional[str] = None
    session_history: Optional[List[Dict]] = None
    training_context: Optional[str] = None
    conversation_examples: Optional[List[Dict]] = None
    emotional_state: Optional[str] = None
    dominant_themes: Optional[List[str]] = None
    therapeutic_approach: Optional[PromptType] = None


class AIPromptManager:
    """
    Gerenciador central dos prompts e regras de resposta da IA.
    Comentários orientam manutenção e extensão.
    """
    def __init__(self):
        pass
    
    # Função de fallback pode ser movida para um utilitário ou arquivo separado se desejar
    def get_fallback_responses(self, risk_level: str, user_context: Optional[Dict] = None) -> List[str]:
        """Retorna respostas estáticas por nível de risco."""
        user_name = user_context['name'].split()[0] if user_context and user_context.get('name') else ""
        name_prefix = f"{user_name}, " if user_name else ""
        fallback_responses = {
            'critical': [
                f"{name_prefix}SITUAÇÃO CRÍTICA DETECTADA! Nossa equipe foi acionada. 🚨",
                f"{name_prefix}TRIAGEM EMERGENCIAL ATIVADA! Profissional em contato. ⚠️",
                f"{name_prefix}VOCÊ NÃO ESTÁ SOZINHO! Atendimento de crise AGORA. 🆘"
            ],
            'high': [
                f"{name_prefix}nossa triagem irá te atender. Você merece suporte! 💪",
                f"{name_prefix}conectando com profissionais. Você tem força! 🌟",
                f"{name_prefix}protocolo de apoio intensivo ativado. Dias melhores virão! ☀️"
            ],
            'moderate': [
                f"{name_prefix}suporte mais direcionado disponível! O que pode fazer hoje? 💭",
                f"{name_prefix}você é forte. Vamos conectar recursos internos? 🌟",
                f"{name_prefix}isso vai passar! Triagem pode organizar acompanhamento. ✨"
            ],
            'low': [
                f"{name_prefix}que bom ter você aqui! Como posso apoiar? 😊",
                f"{name_prefix}oi! Como está se sentindo? 💚",
                f"{name_prefix}estou aqui para ouvir! O que está acontecendo? 🗣️"
            ]
        }
        return fallback_responses.get(risk_level, fallback_responses['low'])
    
    # Métodos de prompt removidos. Toda lógica de prompt está nos arquivos prompts_openai.py e prompts_gemini.py

    def get_sentiment_prompt(self, user_message: str) -> str:
        """
        Gera um prompt simples para análise de sentimento da mensagem do usuário.
        Pode ser customizado para diferentes modelos.
        """
        return f"Analise o sentimento da seguinte mensagem do usuário e responda apenas com uma palavra (positivo, negativo ou neutro):\n{user_message}"

    def build_contextual_prompt(self, context: PromptContext, **kwargs) -> dict:
        """
        Monta um prompt contextualizado básico para fallback ou integração com outros modelos.
        Retorna dicionário compatível com uso esperado (mensagens, max_tokens, temperature).
        """
        prompt = f"Usuário: {context.user_name or 'Desconhecido'}\n"
        prompt += f"Mensagem: {context.user_message}\n"
        prompt += f"Nível de risco: {context.risk_level.value}\n"
        if context.emotional_state:
            prompt += f"Estado emocional: {context.emotional_state}\n"
        if context.dominant_themes:
            prompt += f"Temas principais: {', '.join(context.dominant_themes)}\n"
        prompt += "Responda de forma empática, breve e útil."

        # Estrutura compatível com OpenAI/Gemini
        messages = [
            {"role": "system", "content": "Você é um agente de suporte emocional. Responda de forma empática, breve e útil."},
            {"role": "user", "content": prompt}
        ]
        return {
            "messages": messages,
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.7
        }
    
    # Configurações de provider podem ser movidas para um arquivo utilitário se necessário
    
    # Função de análise de humor pode ser movida para utilitário se desejado
    
    # Função de adaptação pode ser movida para utilitário se desejado
    
    # Validação de tamanho de prompt pode ser utilitário
    
    # Inicialização de templates, estratégias e adaptações removida. Toda lógica de prompt está nos arquivos prompts_openai.py e prompts_gemini.py
    
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
    # (Bloco de fallback removido após unificação do prompt)
    
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


# --- Funções de conveniência ---
def create_prompt_manager() -> AIPromptManager:
    """Cria instância configurada do AIPromptManager."""
    return AIPromptManager()

# Instância global para uso direto
prompt_manager = AIPromptManager()
