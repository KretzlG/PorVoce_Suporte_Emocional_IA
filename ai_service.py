"""
Serviço de IA Emocional usando OpenAI GPT
Responsável por processar mensagens do usuário e fornecer suporte emocional
"""

import os
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class EmotionalAIService:
    def __init__(self):
        """Inicializa o serviço de IA emocional"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-3.5-turbo"
        
        # Prompt base para o agente emocional
        self.system_prompt = """
        Você é um assistente de suporte emocional especializado em oferecer apoio psicológico inicial.
        
        DIRETRIZES IMPORTANTES:
        - Seja empático, acolhedor e não-julgamental
        - Use linguagem simples e acessível
        - Nunca substitua atendimento profissional
        - Sempre encoraje buscar ajuda profissional quando necessário
        - Identifique sinais de risco (autolesão, suicídio) e recomende busca imediata por ajuda
        - Mantenha conversas focadas no bem-estar emocional
        - Não forneça diagnósticos médicos ou psicológicos
        
        NÍVEIS DE RISCO:
        - BAIXO: Tristeza comum, ansiedade leve, estresse cotidiano
        - MODERADO: Ansiedade persistente, humor deprimido, problemas de relacionamento
        - ALTO: Pensamentos de autolesão, ideação suicida, crises de pânico severas
        
        Responda sempre em português brasileiro e termine sua resposta indicando o nível de risco identificado.
        """
        
        # Histórico da conversa
        self.conversation_history: List[Dict] = []
    
    def classify_emotional_risk(self, message: str) -> str:
        """
        Classifica o nível de risco emocional da mensagem
        
        Args:
            message (str): Mensagem do usuário
            
        Returns:
            str: Nível de risco ('baixo', 'moderado', 'alto')
        """
        risk_keywords = {
            'alto': [
                'suicídio', 'me matar', 'acabar com tudo', 'não aguento mais viver',
                'me machucar', 'autolesão', 'cortar', 'morrer', 'desistir da vida',
                'não vale a pena viver', 'quero desaparecer'
            ],
            'moderado': [
                'depressão', 'ansiedade', 'pânico', 'não consigo', 'desesperado',
                'sem esperança', 'sozinho', 'abandonado', 'perdido', 'vazio',
                'insônia', 'não durmo', 'chorar', 'triste sempre'
            ]
        }
        
        message_lower = message.lower()
        
        # Verificar palavras de alto risco
        for keyword in risk_keywords['alto']:
            if keyword in message_lower:
                return 'alto'
        
        # Verificar palavras de risco moderado
        for keyword in risk_keywords['moderado']:
            if keyword in message_lower:
                return 'moderado'
        
        return 'baixo'
    
    def get_ai_response(self, user_message: str) -> Tuple[str, str]:
        """
        Processa mensagem do usuário e retorna resposta da IA e nível de risco
        
        Args:
            user_message (str): Mensagem do usuário
            
        Returns:
            Tuple[str, str]: (resposta_da_ia, nivel_de_risco)
        """
        try:
            # Adicionar mensagem do usuário ao histórico
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Preparar mensagens para a API
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation_history[-10:]  # Manter apenas últimas 10 mensagens
            
            # Fazer chamada para OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Adicionar resposta da IA ao histórico
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Classificar risco
            risk_level = self.classify_emotional_risk(user_message)
            
            return ai_response, risk_level
            
        except Exception as e:
            error_message = f"Desculpe, ocorreu um erro técnico. Por favor, tente novamente. Se o problema persistir, procure ajuda profissional diretamente."
            return error_message, 'baixo'
    
    def get_crisis_response(self) -> str:
        """
        Retorna resposta específica para situações de crise
        
        Returns:
            str: Mensagem de crise com contatos de emergência
        """
        return """
        🚨 ATENÇÃO: Identifiquei que você pode estar passando por uma crise emocional séria.
        
        Por favor, procure ajuda IMEDIATAMENTE:
        
        📞 EMERGÊNCIA:
        • SAMU: 192
        • Bombeiros: 193
        • CVV (Centro de Valorização da Vida): 188
        
        💬 CHAT DE APOIO:
        • CVV: https://www.cvv.org.br/
        
        🏥 Procure também:
        • UPA/Hospital mais próximo
        • CAPS (Centro de Atenção Psicossocial)
        
        Você não está sozinho(a). Existem pessoas prontas para ajudar.
        """
    
    def clear_conversation(self):
        """Limpa o histórico da conversa"""
        self.conversation_history = []
