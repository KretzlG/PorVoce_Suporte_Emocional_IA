# prompts_openai.py
from app.services.ai_prompt import PromptContext, PromptType, RiskLevel
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def build_openai_prompt(context: PromptContext, therapeutic_approach: PromptType) -> Dict:
    """
    Monta o prompt completo para o modelo OpenAI.
    Todos os blocos são explícitos e comentados para facilitar manutenção.
    """
    try:
        # Bloco de apresentação e diretrizes
        prompt = (
            "Você é um agente de suporte emocional, especialista em acolhimento, escuta ativa e intervenção em situações de sofrimento psíquico, risco emocional e crise. Sua missão é oferecer apoio humano, empático e seguro, seguindo as melhores práticas de saúde mental e sempre respeitando o contexto do usuário.\n\n"
            "Diretrizes de apoio emocional:\n"
            "- Escute sem julgar.\n"
            "- Valide os sentimentos do amigo. Diga: 'Você não está sozinho, vamos buscar ajuda juntos.'\n"
            "\nSinais de alerta:\n"
            "- Se afastar dos amigos e da família.\n"
            "- Perder o interesse por coisas que antes gostava.\n"
            "- Ficar desmotivado, descuidar da aparência.\n"
            "- Falar frases como: 'quero sumir', 'não aguento mais'.\n"
            "- Súbito de 'calma' após profunda tristeza.\n"
            "- Despreocupação com autocuidado.\n"
            "\nSituações de risco:\n"
            "- Ter tentado se machucar antes.\n"
            "- Passar por perdas, doenças ou situações muito difíceis.\n"
            "- Sofrer com ansiedade, depressão ou outros transtornos.\n"
            "- Sentir-se sozinho, sem apoio ou sofrer discriminação.\n"
        )

        # Bloco de sistema base (pode ser customizado para OpenAI)
        prompt += f"\n\n{context.system_base if hasattr(context, 'system_base') else ''}"

        # Adaptação por risco
        risk_adaptation = context.risk_adaptation if hasattr(context, 'risk_adaptation') else None
        if risk_adaptation:
            prompt += f"\n\nNÍVEL DE RISCO: {context.risk_level.value.upper()}\nTom da resposta: {risk_adaptation['tone']}\nFoco principal: {risk_adaptation['focus']}\nSugestões prioritárias: {', '.join(risk_adaptation['suggestions'])}"

        # Estratégia terapêutica
        strategy = context.therapeutic_strategy if hasattr(context, 'therapeutic_strategy') else None
        if strategy:
            prompt += f"\n\nABORDAGEM TERAPÊUTICA: {therapeutic_approach.value}\nFoco: {strategy['focus']}\nTécnicas: {', '.join(strategy['techniques'])}\nFrases úteis para incorporar:\n"
            prompt += '\n'.join(['- ' + phrase for phrase in strategy['phrases']])

        # Protocolo de crise
        if context.risk_level == RiskLevel.CRITICAL and hasattr(context, 'risk_critical'):
            prompt += f"\n\n{context.risk_critical}"

        # Dados de treinamento
        if context.training_context:
            prompt += f"\n\n=== CONHECIMENTO ESPECIALIZADO RELEVANTE ===\n{context.training_context}\nINSTRUÇÕES: Use este conhecimento como base científica para sua resposta. Adapte as informações para o contexto do usuário."

        # Exemplos de conversas
        if context.conversation_examples:
            prompt += "\n\n=== EXEMPLOS DE RESPOSTAS EFICAZES ==="
            for i, example in enumerate(context.conversation_examples[:2], 1):
                rating = "⭐" * int(example.get('rating', 3))
                prompt += f"\n💬 Exemplo {i} ({rating}):\nSituação: {example.get('user_message', '')}\nResposta eficaz: {example.get('ai_response', '')}\nPor que funcionou: Abordagem {example.get('risk_level', 'adequada')} para o contexto"
            prompt += "\nInspire-se, mas personalize para o caso atual."

        # Contexto do usuário
        context_info = []
        if context.user_name:
            context_info.append(f"Nome do usuário: {context.user_name}")
        if context.emotional_state:
            context_info.append(f"Estado emocional identificado: {context.emotional_state}")
        if context.dominant_themes:
            context_info.append(f"Temas principais: {', '.join(context.dominant_themes)}")
        if context_info:
            prompt += "\n\nCONTEXTO DO USUÁRIO:\n" + "\n".join(context_info)

        # Instruções finais
        prompt += ("\n\nINSTRUÇÕES FINAIS:\n"
            "1. Responda de forma calorosa e humana\n"
            "2. Use no máximo 200-300 palavras\n"
            "3. Ofereça pelo menos uma sugestão prática\n"
            "4. Termine com uma pergunta aberta ou convite para continuar a conversa\n"
            "5. Se risco alto/crítico, SEMPRE mencione recursos profissionais\n")

        # Histórico da conversa (opcional)
        if context.session_history:
            history_msgs = []
            for msg in context.session_history[-6:]:
                if msg.get('role') in ['user', 'assistant']:
                    history_msgs.append(f"[{msg['role']}]: {msg['content']}")
            if history_msgs:
                prompt += "\n\nHISTÓRICO RECENTE:\n" + "\n".join(history_msgs)

        # Mensagem do usuário
        prompt += f"\n\nMENSAGEM DO USUÁRIO:\n{context.user_message}"

        # Parâmetros
        max_tokens = 400 if context.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else 300
        temperature = 0.7

        return {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}
    except Exception as e:
        logger.error(f"Erro na construção do prompt OpenAI: {e}")
        return {'prompt': 'Erro ao construir prompt.', 'max_tokens': 200, 'temperature': 0.7}
