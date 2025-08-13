"""
Serviço de IA para análise de sentimentos e geração de respostas usando apenas OpenAI
"""

import json
import os
from datetime import datetime


import openai
OPENAI_AVAILABLE = True

class AIService:
	"""Serviço principal de IA para análise emocional e geração de respostas usando apenas OpenAI"""

	def __init__(self, app=None):
		self.openai_client = None
		self.app = app
		self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
		self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 256))
		self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
		openai_api_key = os.getenv("OPENAI_API_KEY")
		if openai_api_key:
			self.openai_client = openai
			self.openai_client.api_key = openai_api_key
		else:
			self.openai_client = None

	def analyze_sentiment(self, text):
		"""Analisa o sentimento do texto usando OpenAI"""
		if not self.openai_client:
			raise RuntimeError("OpenAI não está configurado corretamente.")
		response = self.openai_client.chat.completions.create(
			model=self.openai_model,
			messages=[
				{
					"role": "system",
					"content": (
						"Você é um especialista em análise de sentimento emocional em português brasileiro.\n\n"
						"Analise o texto fornecido e retorne APENAS um JSON válido com:\n"
						"- score: número entre -1 (muito negativo) e 1 (muito positivo)\n"
						"- confidence: número entre 0 e 1 indicando confiança na análise\n"
						"- emotion: uma das seguintes opções: feliz, triste, ansioso, irritado, desesperado, vazio, neutro, esperançoso, calmo\n"
						"- intensity: low, moderate, high\n"
						"Exemplo de resposta: {\"score\": -0.8, \"confidence\": 0.9, \"emotion\": \"triste\", \"intensity\": \"high\"}"
					)
				},
				{"role": "user", "content": f"Analise este texto: {text}"}
			],
			max_tokens=150,
			temperature=0.3
		)
		content = response.choices[0].message.content.strip()
		result = json.loads(content)
		return result

	def generate_response(self, user_message, risk_level='low', user_context=None):
		"""Gera resposta empática usando OpenAI"""
		if not self.openai_client:
			raise RuntimeError("OpenAI não está configurado corretamente.")
		user_name = ""
		if user_context and user_context.get('name'):
			user_name = user_context['name'].split()[0]
		tone_instructions = {
			'low': "Seja empático, acolhedor e encorajador. Use um tom caloroso e de apoio.",
			'moderate': "Seja empático mas mais sério. Demonstre preocupação genuína e ofereça apoio concreto.",
			'high': "Seja muito empático e demonstre preocupação séria. Encoraje buscar ajuda profissional.",
			'critical': "Seja extremamente empático mas firme. Enfatize a urgência de buscar ajuda IMEDIATA."
		}
		system_prompt = (
			f"Você é uma IA de apoio emocional em português brasileiro.\n"
			f"Nível de risco: {risk_level.upper()}.\n"
			f"Instruções: {tone_instructions.get(risk_level, tone_instructions['low'])}\n"
			"Seja empático, acolhedor, objetivo e nunca julgue.\n"
			"Use linguagem natural e humana.\n"
			"Evite conselhos médicos.\n"
			"Valide emoções e ofereça apoio.\n"
			"Responda em até 80 palavras.\n"
			f"{'Use o nome ' + user_name if user_name else ''}"
		)
		response = self.openai_client.chat.completions.create(
			model=self.openai_model,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": f"Mensagem do usuário: {user_message}"}
			],
			max_tokens=self.max_tokens,
			temperature=self.temperature
		)
		ai_response = response.choices[0].message.content.strip()
		return {
			'message': ai_response,
			'risk_level': risk_level,
			'confidence': 0.9,
			'source': 'openai',
			'timestamp': datetime.utcnow().isoformat()
		}

	def get_model_info(self):
		"""Retorna informações sobre o modelo de IA ativo"""
		return {
			'provider': 'OpenAI',
			'active_model': self.openai_model,
			'status': 'active' if self.openai_client else 'inactive',
			'type': 'cloud'
		}
