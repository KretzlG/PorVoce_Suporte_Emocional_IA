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
                'primary': "Seja otimista, encorajadora e energética.",
                'details': "Use energia positiva, foque em soluções e forças da pessoa."
            },
            'moderate': {
                'primary': "Seja compreensiva mas firme e esperançosa.",
                'details': "Valide sentimentos, mas direcione para ação e crescimento."
            },
            'high': {
                'primary': "Seja carinhosa mas direta sobre buscar ajuda.",
                'details': "Transmita urgência com esperança, foque na solução imediata."
            },
            'critical': {
                'primary': "Seja firme, direta e protetiva. Priorize ação IMEDIATA.",
                'details': "Segurança em primeiro lugar. Seja clara sobre necessidade de ajuda profissional AGORA."
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
            'first_interaction_max_words': 40,
            'continuation_max_words': 50,
            'emergency_max_words': 60,
            'temperature_empathetic': 0.8,
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
        
        # Análise dinâmica da conversa
        conversation_mood = self._analyze_conversation_mood(conversation_history)
        adaptation_rules = self._get_adaptation_rules(conversation_mood, risk_level)
        
        # Selecionar template base
        template_type = 'first_interaction' if is_first_message else 'continuation'
        base_template = self.base_prompts[template_type][provider]
        
        # Construir prompt do sistema
        system_prompt = base_template.format(
            risk_level=risk_level.upper(),
            tone_instruction=self.tone_instructions[risk_level]['primary'],
            tone_details=self.tone_instructions[risk_level]['details'],
            user_name_instruction=f"Use {user_name}" if user_name else "",
            max_words=self.response_parameters[f'{template_type}_max_words']
        )
        
        # Adicionar adaptações dinâmicas
        if adaptation_rules:
            system_prompt += f"\n\nADAPTAÇÃO NECESSÁRIA: {adaptation_rules}"
        
        # Adicionar contexto RAG se disponível
        if rag_context:
            system_prompt += f"\n\n{rag_context}"
        
        # Adicionar instruções de emergência para risco crítico
        if risk_level == 'critical':
            system_prompt += self.emergency_prompts['critical_instructions']
        
        # Construir estrutura de mensagens
        if provider == 'openai':
            messages = [{"role": "system", "content": system_prompt}]
            
            # Adicionar histórico limitado (últimas 4 mensagens para manter foco)
            if conversation_history:
                recent_history = conversation_history[-4:]
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
                f"{name_prefix}SITUAÇÃO CRÍTICA DETECTADA! "
                "Nossa equipe especializada foi acionada para te apoiar. 🚨",
                
                f"{name_prefix}TRIAGEM EMERGENCIAL ATIVADA! "
                "Um profissional entrará em contato imediatamente. ⚠️",
                
                f"{name_prefix}VOCÊ NÃO ESTÁ SOZINHO! "
                "Nossa equipe de crise está organizando seu atendimento AGORA. 🆘"
            ],
            
            'high': [
                f"{name_prefix}nossa triagem especializada irá te atender. "
                "Você merece todo o suporte que podemos oferecer! 💪",
                
                f"{name_prefix}conectando você com nossa equipe de profissionais. "
                "Juntos vamos encontrar soluções. Você tem força! 🌟",
                
                f"{name_prefix}acionando protocolo de apoio intensivo. "
                "Nossa plataforma está aqui para você. Dias melhores vão chegar! ☀️"
            ],
            
            'moderate': [
                f"{name_prefix}nossa equipe pode te oferecer suporte mais direcionado! "
                "O que você pode fazer hoje para se cuidar melhor? 💭",
                
                f"{name_prefix}você é mais forte do que imagina. "
                "Vamos conectar você com recursos internos que podem ajudar? 🌟",
                
                f"{name_prefix}isso vai passar! Nossa triagem pode organizar "
                "um acompanhamento personalizado para você. ✨"
            ],
            
            'low': [
                f"{name_prefix}que bom ter você aqui! "
                "Conte-me como posso te apoiar hoje. 😊",
                
                f"{name_prefix}oi! Como você está se sentindo agora? 💚",
                
                f"{name_prefix}estou aqui para te ouvir! "
                "O que está acontecendo? 🗣️"
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
                'triagem_interna': "Triagem Especializada - Equipe interna disponível 24h",
                'samu': "SAMU: 192 (emergências médicas)",
                'emergency': "Em emergência: vá ao hospital mais próximo"
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
