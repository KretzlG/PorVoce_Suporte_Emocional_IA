"""
Sistema de Prompts Profissional para IA de Suporte Emocional
Centraliza todos os prompts, instruções e configurações de tom

"""

from typing import Dict, Optional, List
from datetime import datetime


class AIPromptManager:
    """
    Gerenciador Central de Prompts para Suporte Emocional
    
    Funcionalidades:
    - Prompts personalizados por nível de risco
    - Instruções específicas para primeira conversa vs continuação
    - Templates de sistema para análise de sentimento
    - Configurações de tom e comportamento
    - Prompts para diferentes providers (OpenAI, Gemini, etc.)
    """
    
    def __init__(self):
        """Inicializa o gerenciador com todos os prompts organizados"""
        
        # === PROMPTS PARA ANÁLISE DE SENTIMENTO ===
        self.sentiment_analysis_prompts = {
            'openai_system': (
                "Você é um especialista em análise de sentimento emocional em português brasileiro.\n"
                "Analise o texto e retorne APENAS um JSON válido:\n"
                "{\n"
                '  "score": número entre -1 (muito negativo) e 1 (muito positivo),\n'
                '  "confidence": número entre 0 e 1,\n'
                '  "emotion": "feliz|triste|ansioso|irritado|desesperado|vazio|neutro|esperançoso|calmo",\n'
                '  "intensity": "low|moderate|high"\n'
                "}\n\n"
                "IMPORTANTE:\n"
                "- Seja preciso na análise emocional\n"
                "- Considere contexto cultural brasileiro\n" 
                "- Detecte sutilezas e entrelinhas\n"
                "- Priorize segurança em casos ambíguos"
            ),
            
            'gemini_system': (
                "Analise o sentimento emocional deste texto em português brasileiro.\n"
                "Retorne um JSON com:\n"
                "- score: -1 a 1 (negativo/positivo)\n"
                "- confidence: 0 a 1\n"
                "- emotion: feliz, triste, ansioso, irritado, desesperado, vazio, neutro, esperançoso, calmo\n"
                "- intensity: low, moderate, high\n"
                "Seja preciso e considere o contexto cultural brasileiro."
            )
        }
        
        # === INSTRUÇÕES DE TOM POR NÍVEL DE RISCO ===
        self.tone_instructions = {
            'low': {
                'primary': "Seja empático, acolhedor e encorajador.",
                'details': "Mantenha tom leve e positivo, oferecendo suporte sem dramatizar."
            },
            'moderate': {
                'primary': "Seja empático e demonstre preocupação genuína.",
                'details': "Mostre compreensão, valide sentimentos, sugira estratégias práticas."
            },
            'high': {
                'primary': "Seja muito empático e encoraje buscar ajuda profissional.",
                'details': "Transmita urgência sem assustar, sugira recursos concretos."
            },
            'critical': {
                'primary': "Seja extremamente empático mas firme. Enfatize urgência de ajuda IMEDIATA.",
                'details': "Priorize segurança, seja direto sobre necessidade de ajuda profissional."
            }
        }
        
        # === PROMPTS BASE PARA DIFERENTES SITUAÇÕES ===
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
        
        # === PROMPTS DE EMERGÊNCIA ===
        self.emergency_prompts = self._get_emergency_prompts()
        
        # === CONFIGURAÇÕES DE PARÂMETROS ===
        self.response_parameters = {
            'first_interaction_max_words': 80,
            'continuation_max_words': 100,
            'emergency_max_words': 120,
            'temperature_empathetic': 0.7,
            'temperature_analytical': 0.3
        }
    
    def get_sentiment_prompt(self, provider: str = 'openai') -> str:
        """
        Retorna prompt para análise de sentimento
        
        Args:
            provider: 'openai' ou 'gemini'
            
        Returns:
            String com prompt formatado para análise de sentimento
        """
        return self.sentiment_analysis_prompts.get(f'{provider}_system', 
                                                  self.sentiment_analysis_prompts['openai_system'])
    
    def build_conversation_prompt(self, 
                                user_message: str,
                                risk_level: str,
                                provider: str = 'openai',
                                user_context: Optional[Dict] = None,
                                conversation_history: Optional[List] = None,
                                rag_context: Optional[str] = None,
                                is_first_message: bool = False) -> Dict:
        """
        Constrói prompt completo para geração de resposta
        
        Args:
            user_message: Mensagem do usuário
            risk_level: Nível de risco detectado
            provider: Provider de IA ('openai', 'gemini')
            user_context: Contexto do usuário
            conversation_history: Histórico da conversa
            rag_context: Contexto do sistema RAG
            is_first_message: Se é primeira interação
            
        Returns:
            Dict com prompt estruturado e metadados
        """
        # Extrair nome do usuário
        user_name = ""
        if user_context and user_context.get('name'):
            user_name = user_context['name'].split()[0]
        
        # Selecionar template base
        template_type = 'first_interaction' if is_first_message else 'continuation'
        base_template = self.base_prompts[template_type][provider]
        
        # Construir prompt do sistema
        system_prompt = base_template.format(
            risk_level=risk_level.upper(),
            tone_instruction=self.tone_instructions[risk_level]['primary'],
            tone_details=self.tone_instructions[risk_level]['details'],
            user_name_instruction=f"Use o nome {user_name}" if user_name else "",
            max_words=self.response_parameters[f'{template_type}_max_words']
        )
        
        # Adicionar contexto RAG se disponível
        if rag_context:
            system_prompt += f"\n\n{rag_context}"
        
        # Adicionar instruções de emergência para risco crítico
        if risk_level == 'critical':
            system_prompt += self.emergency_prompts['critical_instructions']
        
        # Construir estrutura de mensagens
        if provider == 'openai':
            messages = [{"role": "system", "content": system_prompt}]
            
            # Adicionar histórico limitado (últimas 6 mensagens)
            if conversation_history:
                recent_history = conversation_history[-6:]
                for msg in recent_history:
                    role = "user" if msg.get('message_type') == 'USER' else "assistant"
                    messages.append({"role": role, "content": msg.get('content', '')})
            
            # Mensagem atual
            messages.append({"role": "user", "content": user_message})
            
            return {
                'messages': messages,
                'temperature': self.response_parameters['temperature_empathetic'],
                'max_tokens': self._calculate_max_tokens(template_type, risk_level)
            }
        
        elif provider == 'gemini':
            # Gemini usa prompt único
            full_prompt = f"{system_prompt}\n\nMensagem do usuário: {user_message}"
            
            return {
                'prompt': full_prompt,
                'temperature': self.response_parameters['temperature_empathetic']
            }
        
        else:
            raise ValueError(f"Provider '{provider}' não suportado")
    
    def get_fallback_responses(self, risk_level: str, user_context: Optional[Dict] = None) -> List[str]:
        """
        Retorna respostas estáticas organizadas por nível de risco
        
        Args:
            risk_level: Nível de risco detectado
            user_context: Contexto do usuário para personalização
            
        Returns:
            Lista de possíveis respostas estáticas
        """
        user_name = ""
        if user_context and user_context.get('name'):
            user_name = user_context['name'].split()[0]
            name_prefix = f"{user_name}, " if user_name else ""
        else:
            name_prefix = ""
        
        fallback_responses = {
            'critical': [
                f"{name_prefix}estou muito preocupada com você. Por favor, busque ajuda IMEDIATAMENTE. "
                "Ligue para o CVV: 188 (24h) ou vá ao hospital. Você não está sozinho(a). 🚨",
                
                f"{name_prefix}percebo que você está em uma situação muito difícil. "
                "É URGENTE que procure ajuda profissional agora. CVV: 188 (24h). Não hesite! ⚠️",
                
                f"{name_prefix}sua segurança é prioridade. Ligue AGORA para o CVV: 188 "
                "ou procure o hospital mais próximo. Você merece ajuda e apoio. 🆘"
            ],
            
            'high': [
                f"{name_prefix}percebo que você está passando por um momento muito difícil. "
                "Considere conversar com um profissional ou ligar para o CVV: 188. 📞",
                
                f"{name_prefix}estou preocupada com como você está se sentindo. "
                "Buscar ajuda profissional pode fazer muita diferença. CVV: 188 está sempre disponível. 💙",
                
                f"{name_prefix}suas palavras mostram uma dor profunda. "
                "Por favor, considere falar com um psicólogo ou ligar para o CVV: 188. Você não está sozinho(a). 🤝"
            ],
            
            'moderate': [
                f"{name_prefix}entendo que as coisas estão pesadas para você. "
                "Lembre-se que é normal ter altos e baixos. Quer conversar sobre isso? 💭",
                
                f"{name_prefix}percebo que você está enfrentando desafios. "
                "Às vezes ajuda falar sobre o que está sentindo. Estou aqui para te ouvir. 👂",
                
                f"{name_prefix}momentos difíceis fazem parte da vida, mas não precisamos enfrentá-los sozinhos. "
                "Como posso te apoiar hoje? 🌟"
            ],
            
            'low': [
                f"{name_prefix}estou aqui para te ouvir e apoiar. Como posso te ajudar hoje? 😊",
                
                f"{name_prefix}que bom ter você aqui! Conte-me o que está em sua mente. 💚",
                
                f"{name_prefix}estou disponível para conversar sobre qualquer coisa que queira compartilhar. "
                "O que gostaria de falar? 🗣️"
            ]
        }
        
        return fallback_responses.get(risk_level, fallback_responses['low'])
    
    def _get_first_interaction_prompt_openai(self) -> str:
        """Template para primeira interação - OpenAI"""
        return """Você é Íris, uma IA de apoio emocional especializada em português brasileiro.

CONTEXTO: PRIMEIRA interação com este usuário
NÍVEL DE RISCO: {risk_level}
INSTRUÇÃO DE TOM: {tone_instruction}
DETALHES: {tone_details}

DIRETRIZES PARA PRIMEIRA CONVERSA:
- Apresente-se brevemente como Íris
- Demonstre interesse genuíno e empatia
- Seja acolhedora e não julgue
- Ofereça apoio imediato
- Crie ambiente seguro para compartilhamento
- {user_name_instruction}

LIMITE: Responda em até {max_words} palavras
ESTILO: Natural, empático, brasileiro"""
    
    def _get_continuation_prompt_openai(self) -> str:
        """Template para continuação de conversa - OpenAI"""
        return """Você é Íris, continuando uma conversa de apoio emocional.

CONTEXTO: CONTINUAÇÃO da conversa
NÍVEL DE RISCO: {risk_level}
INSTRUÇÃO DE TOM: {tone_instruction}
DETALHES: {tone_details}

DIRETRIZES PARA CONTINUAÇÃO:
- Continue naturalmente, SEM se apresentar novamente
- Mantenha consistência com conversas anteriores
- Seja empática e ofereça apoio específico
- Faça perguntas abertas quando apropriado
- Valide sentimentos do usuário
- {user_name_instruction}

LIMITE: Responda em até {max_words} palavras
ESTILO: Natural, empático, consistente"""
    
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
- Mencione CVV: 188 (24 horas)
- Sugira procurar hospital/pronto-socorro
- Seja firme mas empático
- NÃO minimize a situação
- Priorize segurança acima de tudo""",
            
            'crisis_contacts': {
                'cvv': "CVV - Centro de Valorização da Vida: 188 (24h)",
                'samu': "SAMU: 192 (emergências médicas)",
                'emergency': "Em emergência: vá ao hospital mais próximo"
            }
        }
    
    def _calculate_max_tokens(self, template_type: str, risk_level: str) -> int:
        """Calcula número máximo de tokens baseado no contexto"""
        base_tokens = {
            'first_interaction': 120,
            'continuation': 150
        }
        
        # Aumentar tokens para situações críticas
        if risk_level == 'critical':
            return base_tokens.get(template_type, 150) + 50
        elif risk_level == 'high':
            return base_tokens.get(template_type, 150) + 30
        else:
            return base_tokens.get(template_type, 150)
    
    def get_provider_config(self, provider: str) -> Dict:
        """
        Retorna configurações específicas por provider
        
        Args:
            provider: Nome do provider ('openai', 'gemini')
            
        Returns:
            Dict com configurações do provider
        """
        configs = {
            'openai': {
                'supports_system_message': True,
                'supports_conversation_history': True,
                'max_context_messages': 6,
                'preferred_temperature': 0.7,
                'supports_json_mode': True
            },
            'gemini': {
                'supports_system_message': False,
                'supports_conversation_history': False,
                'max_context_messages': 0,
                'preferred_temperature': 0.7,
                'supports_json_mode': False
            }
        }
        
        return configs.get(provider, configs['openai'])
    
    def validate_prompt_length(self, prompt: str, provider: str) -> bool:
        """
        Valida se o prompt está dentro dos limites do provider
        
        Args:
            prompt: Texto do prompt
            provider: Nome do provider
            
        Returns:
            True se válido, False caso contrário
        """
        limits = {
            'openai': 8000,  # Aproximadamente para gpt-4o-mini
            'gemini': 6000   # Aproximadamente para gemini-pro
        }
        
        # Estimativa simples: 4 caracteres por token
        estimated_tokens = len(prompt) // 4
        
        return estimated_tokens <= limits.get(provider, 8000)


# === FUNÇÕES DE CONVENIÊNCIA ===

def create_prompt_manager() -> AIPromptManager:
    """Cria instância configurada do AIPromptManager"""
    return AIPromptManager()

# Instância global para uso direto
prompt_manager = AIPromptManager()
