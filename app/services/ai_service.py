"""
Serviço de IA para análise de sentimentos e geração de respostas usando apenas OpenAI
"""

import json
import os
from datetime import datetime, UTC



import openai
OPENAI_AVAILABLE = True

# Gemini e BERT placeholders
try:
	import google.generativeai as genai
	GEMINI_AVAILABLE = True
except ImportError:
	GEMINI_AVAILABLE = False

try:
	from transformers import pipeline
	BERT_AVAILABLE = True
except ImportError:
	BERT_AVAILABLE = False

import random


class AIService:
	"""Serviço principal de IA para análise emocional e geração de respostas com fallback LLM"""

	def __init__(self, app=None):
		self.app = app
		# OpenAI
		self.openai_client = None
		self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
		self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 256))
		self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
		openai_api_key = os.getenv("OPENAI_API_KEY")
		if openai_api_key:
			self.openai_client = openai
			self.openai_client.api_key = openai_api_key
		else:
			self.openai_client = None

		# Gemini
		self.gemini_client = None
		self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
		gemini_api_key = os.getenv("GEMINI_API_KEY")
		if GEMINI_AVAILABLE and gemini_api_key:
			genai.configure(api_key=gemini_api_key)
			self.gemini_client = genai
		else:
			self.gemini_client = None

		# BERT
		self.bert_pipeline = None
		if BERT_AVAILABLE:
			try:
				self.bert_pipeline = pipeline("text-generation", model="neuralmind/bert-base-portuguese-cased")
			except Exception:
				self.bert_pipeline = None

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


	def generate_response(self, user_message, risk_level='low', user_context=None, conversation_history=None, fallback=True):
		"""Gera resposta empática usando LLMs com fallback automático"""
		errors = []
		# 1. OpenAI
		if self.openai_client:
			try:
				return self._generate_response_openai(user_message, risk_level, user_context, conversation_history)
			except Exception as e:
				errors.append(f"OpenAI: {str(e)}")
		# 2. Gemini
		if self.gemini_client:
			try:
				return self._generate_response_gemini(user_message, risk_level, user_context)
			except Exception as e:
				errors.append(f"Gemini: {str(e)}")
		# 3. BERT
		if self.bert_pipeline:
			try:
				return self._generate_response_bert(user_message, risk_level, user_context)
			except Exception as e:
				errors.append(f"BERT: {str(e)}")
		# 4. Resposta fixa
		return self._generate_response_fallback(user_message, risk_level, user_context, errors)

	def _generate_response_openai(self, user_message, risk_level, user_context, conversation_history=None):
		user_name = ""
		if user_context and user_context.get('name'):
			user_name = user_context['name'].split()[0]
		
		# Verificar se é a primeira mensagem da conversa
		is_first_message = not conversation_history or len(conversation_history) == 0
		
		tone_instructions = {
			'low': "Seja empático, acolhedor e encorajador. Use um tom caloroso e de apoio.",
			'moderate': "Seja empático mas mais sério. Demonstre preocupação genuína e ofereça apoio concreto.",
			'high': "Seja muito empático e demonstre preocupação séria. Encoraje buscar ajuda profissional.",
			'critical': "Seja extremamente empático mas firme. Enfatize a urgência de buscar ajuda IMEDIATA."
		}
		
		# Prompt diferente para primeira mensagem vs continuação
		if is_first_message:
			system_prompt = (
				f"Você é Íris, uma IA de apoio emocional em português brasileiro.\n"
				f"Esta é a PRIMEIRA interação com o usuário.\n"
				f"Nível de risco: {risk_level.upper()}.\n"
				f"Instruções: {tone_instructions.get(risk_level, tone_instructions['low'])}\n"
				"Apresente-se brevemente como Íris e ofereça apoio.\n"
				"Seja empático, acolhedor, objetivo e nunca julgue.\n"
				"Use linguagem natural e humana.\n"
				"Evite conselhos médicos.\n"
				"Responda em até 60 palavras.\n"
				f"{'Use o nome ' + user_name if user_name else ''}"
			)
		else:
			system_prompt = (
				f"Você é Íris, uma IA de apoio emocional em português brasileiro.\n"
				f"Esta é uma CONTINUAÇÃO da conversa (NÃO se apresente novamente).\n"
				f"Nível de risco: {risk_level.upper()}.\n"
				f"Instruções: {tone_instructions.get(risk_level, tone_instructions['low'])}\n"
				"Continue a conversa naturalmente, SEM se apresentar.\n"
				"Seja empático, acolhedor, objetivo e nunca julgue.\n"
				"Use linguagem natural e humana.\n"
				"Evite conselhos médicos.\n"
				"Valide emoções e ofereça apoio específico.\n"
				"Responda em até 80 palavras.\n"
				f"{'Use o nome ' + user_name if user_name else ''}"
			)
		
		# Construir mensagens do contexto
		messages = [{"role": "system", "content": system_prompt}]
		
		# Adicionar histórico limitado se disponível
		if conversation_history and len(conversation_history) > 0:
			# Pegar as últimas 4 mensagens para contexto
			recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
			for msg in recent_history:
				role = "user" if msg.get('message_type') == 'USER' else "assistant"
				messages.append({"role": role, "content": msg.get('content', '')})
		
		# Adicionar mensagem atual do usuário
		messages.append({"role": "user", "content": user_message})
		
		response = self.openai_client.chat.completions.create(
			model=self.openai_model,
			messages=messages,
			max_tokens=self.max_tokens,
			temperature=self.temperature
		)
		ai_response = response.choices[0].message.content.strip()
		return {
			'message': ai_response,
			'risk_level': risk_level,
			'confidence': 0.9,
			'source': 'openai',
			'timestamp': datetime.now(UTC).isoformat()
		}

	def _generate_response_gemini(self, user_message, risk_level, user_context):
		# Placeholder Gemini (Google Generative AI)
		user_name = ""
		if user_context and user_context.get('name'):
			user_name = user_context['name'].split()[0]
		prompt = (
			f"Você é uma IA de apoio emocional em português brasileiro.\n"
			f"Nível de risco: {risk_level.upper()}.\n"
			f"Mensagem do usuário: {user_message}\n"
			f"{'Use o nome ' + user_name if user_name else ''}\n"
			"Seja empático, acolhedor, objetivo e nunca julgue.\n"
			"Use linguagem natural e humana.\n"
			"Evite conselhos médicos.\n"
			"Valide emoções e ofereça apoio.\n"
			"Responda em até 80 palavras."
		)
		model = self.gemini_client.GenerativeModel(self.gemini_model)
		response = model.generate_content(prompt)
		ai_response = response.text.strip()
		return {
			'message': ai_response,
			'risk_level': risk_level,
			'confidence': 0.85,
			'source': 'gemini',
			'timestamp': datetime.now(UTC).isoformat()
		}

	def _generate_response_bert(self, user_message, risk_level, user_context):
		# BERT não é ideal para geração, mas pode ser usado como fallback simples
		user_name = ""
		if user_context and user_context.get('name'):
			user_name = user_context['name'].split()[0]
		prompt = (
			f"Mensagem do usuário: {user_message}\n"
			f"{'Use o nome ' + user_name if user_name else ''}\n"
			"Seja empático, acolhedor, objetivo e nunca julgue.\n"
			"Responda em até 80 palavras."
		)
		result = self.bert_pipeline(prompt, max_length=80, num_return_sequences=1)
		ai_response = result[0]['generated_text'].strip()
		return {
			'message': ai_response,
			'risk_level': risk_level,
			'confidence': 0.7,
			'source': 'bert',
			'timestamp': datetime.now(UTC).isoformat()
		}

	def _generate_response_fallback(self, user_message, risk_level, user_context, errors=None):
		# Respostas fixas para fallback final
		respostas = [
			"Sinto muito, estou com dificuldades técnicas no momento. Mas estou aqui para te ouvir. Como você está se sentindo?",
			"No momento não consigo acessar todos os meus recursos, mas quero te apoiar. Pode me contar mais?",
			"Estou com instabilidade, mas quero te ouvir. Fique à vontade para compartilhar o que está sentindo.",
			"Desculpe, estou com problemas técnicos. Se quiser conversar, estou aqui para te escutar."
		]
		msg = random.choice(respostas)
		return {
			'message': msg,
			'risk_level': risk_level,
			'confidence': 0.3,
			'source': 'fallback',
			'timestamp': datetime.now(UTC).isoformat(),
			'errors': errors or []
		}

	def get_model_info(self):
		"""Retorna informações sobre o modelo de IA ativo e fallback"""
		info = []
		info.append({
			'provider': 'OpenAI',
			'active_model': self.openai_model,
			'status': 'active' if self.openai_client else 'inactive',
			'type': 'cloud'
		})
		info.append({
			'provider': 'Gemini',
			'active_model': self.gemini_model,
			'status': 'active' if self.gemini_client else 'inactive',
			'type': 'cloud'
		})
		info.append({
			'provider': 'BERT',
			'active_model': 'neuralmind/bert-base-portuguese-cased',
			'status': 'active' if self.bert_pipeline else 'inactive',
			'type': 'local'
		})
		info.append({
			'provider': 'Fallback',
			'active_model': 'respostas fixas',
			'status': 'always',
			'type': 'static'
		})
		return info
