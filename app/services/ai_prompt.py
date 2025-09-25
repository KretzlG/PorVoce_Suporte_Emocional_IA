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
        # Templates e estratégias
        self.prompt_templates = self._initialize_templates()
        self.therapeutic_strategies = self._initialize_therapeutic_strategies()
        self.risk_adaptations = self._initialize_risk_adaptations()

        # Prompts para análise de sentimento
        self.sentiment_analysis_prompts = {
            'openai_system': (
                "Você é um especialista em análise de sentimento emocional em português brasileiro.\n"
                "Retorne APENAS um JSON válido com score, confidence, emotion e intensity.\n"
                "Considere contexto cultural brasileiro e priorize segurança."
            ),
            'gemini_system': (
                "Analise o sentimento emocional em português brasileiro.\n"
                "Retorne JSON com score, confidence, emotion e intensity."
            )
        }

        # Instruções de tom por nível de risco
        self.tone_instructions = {
            'low': {'primary': "Seja otimista.", 'details': "Energia positiva."},
            'moderate': {'primary': "Compreensiva e firme.", 'details': "Valide e direcione."},
            'high': {'primary': "Carinhosa e direta.", 'details': "Urgência com esperança."},
            'critical': {'primary': "Firme e protetiva.", 'details': "Segurança em primeiro lugar."}
        }

        # Prompts base para situações
        self.base_prompts = {
            'first_interaction': {
                'openai': self._get_first_interaction_prompt_openai(),
                'gemini': self._get_first_interaction_prompt_gemini()
            },
            'continuation': {
                'openai': self._get_continuation_prompt_openai(),
                'gemini': self._get_continuation_prompt_gemini()
            }
        }

        # Prompts de emergência
        self.emergency_prompts = self._get_emergency_prompts()

        # Parâmetros de resposta
        self.response_parameters = {
            'first_interaction_max_words': 40,
            'continuation_max_words': 50,
            'emergency_max_words': 60,
            'temperature_empathetic': 0.8,
            'temperature_analytical': 0.3
        }
    
    # --- Métodos principais ---
    def get_sentiment_prompt(self, provider: str = 'openai') -> str:
        """Retorna prompt para análise de sentimento."""
        return self.sentiment_analysis_prompts.get(f'{provider}_system', self.sentiment_analysis_prompts['openai_system'])
    
    def build_contextual_prompt(self, context: PromptContext, provider: str = 'openai') -> Dict:
        """Constrói prompt contextualizado baseado no contexto fornecido."""
        try:
            therapeutic_approach = self._determine_therapeutic_approach(context)
            prompt_sections = self._build_prompt_sections(context, therapeutic_approach)
            if context.training_context:
                prompt_sections['training_integration'] = self._integrate_training_data(context.training_context, context.risk_level)
            if context.conversation_examples:
                prompt_sections['conversation_examples'] = self._format_conversation_examples(context.conversation_examples, context.risk_level)
            if provider == 'openai':
                return self._build_openai_prompt(prompt_sections, context)
            elif provider == 'gemini':
                return self._build_gemini_prompt(prompt_sections, context)
            else:
                return self._build_generic_prompt(prompt_sections, context)
        except Exception as e:
            logger.error(f"Erro na construção do prompt: {e}")
            return self._build_fallback_prompt(context, provider)
    
    def build_conversation_prompt(self, user_message: str, risk_level: str, provider: str = 'openai', user_context: Optional[Dict] = None, conversation_history: Optional[List] = None, rag_context: Optional[str] = None, is_first_message: bool = False) -> Dict:
        """Constrói prompt completo para geração de resposta."""
        user_name = user_context['name'].split()[0] if user_context and user_context.get('name') else ""
        conversation_mood = self._analyze_conversation_mood(conversation_history)
        adaptation_rules = self._get_adaptation_rules(conversation_mood, risk_level)
        template_type = 'first_interaction' if is_first_message else 'continuation'
        base_template = self.base_prompts[template_type][provider]
        system_prompt = base_template.format(
            risk_level=risk_level.upper(),
            tone_instruction=self.tone_instructions[risk_level]['primary'],
            tone_details=self.tone_instructions[risk_level]['details'],
            user_name_instruction=f"Use {user_name}" if user_name else "",
            max_words=self.response_parameters[f'{template_type}_max_words']
        )
        if adaptation_rules:
            system_prompt += f"\n\nADAPTAÇÃO: {adaptation_rules}"
        if rag_context:
            system_prompt += f"\n\n{rag_context}"
        if risk_level == 'critical':
            system_prompt += self.emergency_prompts['critical_instructions']
        if provider == 'openai':
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                for msg in conversation_history[-4:]:
                    role = "user" if msg.get('message_type') == 'USER' else "assistant"
                    messages.append({"role": role, "content": msg.get('content', '')})
            messages.append({"role": "user", "content": user_message})
            return {
                'messages': messages,
                'temperature': self.response_parameters['temperature_empathetic'],
                'max_tokens': self._calculate_max_tokens(template_type, risk_level)
            }
        elif provider == 'gemini':
            full_prompt = f"{system_prompt}\n\nMensagem do usuário: {user_message}"
            return {
                'prompt': full_prompt,
                'temperature': self.response_parameters['temperature_empathetic']
            }
        else:
            raise ValueError(f"Provider '{provider}' não suportado")
    
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
    
    def _get_first_interaction_prompt_openai(self) -> str:
        """Template para primeira interação - OpenAI"""
        return """Você é Íris, assistente de apoio emocional brasileira.

PRIMEIRA CONVERSA | RISCO: {risk_level}
{tone_instruction} {tone_details}

REGRAS RÍGIDAS:
- NUNCA se apresente após a primeira frase
- NUNCA peça desculpas desnecessariamente  
- NUNCA diga "entendo que", "sei que é difícil"
- FOQUE na pessoa, não em você
- Seja DIRETA e PRÁTICA
- Use energia POSITIVA sempre que possível
{user_name_instruction}

MÁXIMO {max_words} palavras. Seja concisa e eficaz."""
    
    def _get_continuation_prompt_openai(self) -> str:
        """Template para continuação de conversa - OpenAI"""
        return """Continue como Íris em conversa em andamento.

CONVERSA CONTINUADA | RISCO: {risk_level}
{tone_instruction} {tone_details}

REGRAS OBRIGATÓRIAS:
- NUNCA se apresente novamente
- NUNCA repita frases como "estou aqui para", "sinto muito"
- Responda DIRETAMENTE ao que foi dito
- Adapte seu tom ao ESTADO EMOCIONAL atual
- Seja PRÁTICA e SOLUCIONADORA
- Use ENERGIA para motivar
- ENCORAJE a buscar ajuda profissional através da rota de triagem
{user_name_instruction}

MÁXIMO {max_words} palavras. Vá direto ao ponto."""
    
    def _get_first_interaction_prompt_gemini(self) -> str:
        """Template para primeira interação - Gemini"""
        return """Você é Íris, IA de apoio emocional em português brasileiro.

PRIMEIRA conversa. RISCO: {risk_level}
{tone_instruction} {tone_details}

Apresente-se brevemente e seja acolhedora.
{user_name_instruction}
Máximo {max_words} palavras."""
    
    def _get_continuation_prompt_gemini(self) -> str:
        """Template para continuação - Gemini"""
        return """Você é Íris, continuando conversa de apoio emocional.

RISCO: {risk_level}
{tone_instruction} {tone_details}

Continue naturalmente, sem se apresentar.
{user_name_instruction}
Máximo {max_words} palavras."""
    
    def _get_emergency_prompts(self) -> Dict:
        """Prompts específicos para situações de emergência"""
        return {
            'critical_instructions': """

⚠️ SITUAÇÃO DE RISCO CRÍTICO DETECTADA:
- Enfatize urgência de ajuda IMEDIATA
- Ative triagem emergencial interna
- Sugira procurar hospital/pronto-socorro
- Seja firme mas empático
- NÃO minimize a situação
- Priorize segurança acima de tudo""",
            
            'crisis_contacts': {
                'triagem_interna': "Triagem Especializada - Equipe interna disponível 24h"
            }
        }
    
    def _calculate_max_tokens(self, template_type: str, risk_level: str) -> int:
        """Calcula número máximo de tokens baseado no contexto"""
        base_tokens = {
            'first_interaction': 80,
            'continuation': 100
        }
        
        # Aumentar tokens apenas para situações críticas
        if risk_level == 'critical':
            return base_tokens.get(template_type, 100) + 30
        elif risk_level == 'high':
            return base_tokens.get(template_type, 100) + 20
        else:
            return base_tokens.get(template_type, 100)
    
    def get_provider_config(self, provider: str) -> Dict:
        """Retorna configurações específicas por provider."""
        configs = {
            'openai': {'supports_system_message': True, 'supports_conversation_history': True, 'max_context_messages': 6, 'preferred_temperature': 0.7, 'supports_json_mode': True},
            'gemini': {'supports_system_message': False, 'supports_conversation_history': False, 'max_context_messages': 0, 'preferred_temperature': 0.7, 'supports_json_mode': False}
        }
        return configs.get(provider, configs['openai'])
    
    def _analyze_conversation_mood(self, conversation_history: Optional[List]) -> str:
        """
        Analisa o humor geral da conversa para adaptação dinâmica
        
        Args:
            conversation_history: Histórico das mensagens
            
        Returns:
            String indicando o humor: 'improving', 'worsening', 'stable', 'crisis', 'unknown'
        """
        if not conversation_history or len(conversation_history) < 3:
            return 'unknown'
        
        try:
            # Analisa as últimas 4 mensagens do usuário
            user_messages = [
                msg for msg in conversation_history[-6:] 
                if msg.get('message_type') == 'USER'
            ][-4:]
            
            if len(user_messages) < 2:
                return 'unknown'
            
            # Palavras que indicam melhora
            improvement_words = [
                'melhor', 'melhorando', 'obrigado', 'ajudou', 'consegui', 
                'tentando', 'força', 'esperança', 'positivo', 'bem'
            ]
            
            # Palavras que indicam piora
            worsening_words = [
                'pior', 'piorando', 'desistir', 'acabou', 'impossível', 
                'não aguento', 'sem saída', 'desespero', 'vazio'
            ]
            
            # Palavras de crise
            crisis_words = [
                'morrer', 'suicídio', 'acabar com tudo', 'não quero viver',
                'me matar', 'melhor morto'
            ]
            
            improvement_score = 0
            worsening_score = 0
            crisis_score = 0
            
            for msg in user_messages:
                content = msg.get('content', '').lower()
                
                improvement_score += sum(1 for word in improvement_words if word in content)
                worsening_score += sum(1 for word in worsening_words if word in content)
                crisis_score += sum(1 for word in crisis_words if word in content)
            
            # Determinar humor
            if crisis_score > 0:
                return 'crisis'
            elif improvement_score > worsening_score:
                return 'improving'
            elif worsening_score > improvement_score:
                return 'worsening'
            else:
                return 'stable'
                
        except Exception:
            return 'unknown'
    
    def _get_adaptation_rules(self, conversation_mood: str, risk_level: str) -> str:
        """
        Retorna regras de adaptação baseadas no humor da conversa
        
        Args:
            conversation_mood: Humor detectado da conversa
            risk_level: Nível de risco atual
            
        Returns:
            String com regras específicas de adaptação
        """
        adaptations = {
            'improving': "Pessoa está melhorando! Reforce progresso, seja AINDA MAIS POSITIVA e encorajadora. Celebre pequenas vitórias!",
            
            'worsening': "Situação piorando. Seja mais FIRME e DIRETA sobre buscar ajuda. Aumente energia positiva para contrabalançar.",
            
            'crisis': "CRISE DETECTADA. Seja EXTREMAMENTE DIRETA sobre buscar ajuda IMEDIATA. Priorize segurança acima de tudo.",
            
            'stable': "Conversa estável. Mantenha tom consistente e foque em pequenos passos para frente.",
            
            'unknown': "Primeira conversa ou dados insuficientes. Seja calorosa mas não excessiva."
        }
        
        adaptation = adaptations.get(conversation_mood, '')
        
        # Ajustes específicos por risco
        if risk_level == 'critical' and conversation_mood != 'improving':
            adaptation += " REFORCE urgência de ajuda profissional."
        elif risk_level == 'low' and conversation_mood == 'improving':
            adaptation += " Use mais humor e leveza."
            
        return adaptation
    
    def validate_prompt_length(self, prompt: str, provider: str) -> bool:
        """Valida se o prompt está dentro dos limites do provider."""
        limits = {'openai': 8000, 'gemini': 6000}
        estimated_tokens = len(prompt) // 4
        return estimated_tokens <= limits.get(provider, 8000)
    
    # === MÉTODOS AVANÇADOS (INTEGRADOS DO ADVANCED PROMPT ENGINEER) ===
    
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


# --- Funções de conveniência ---
def create_prompt_manager() -> AIPromptManager:
    """Cria instância configurada do AIPromptManager."""
    return AIPromptManager()

# Instância global para uso direto
prompt_manager = AIPromptManager()
