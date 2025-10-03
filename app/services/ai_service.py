"""
Serviço Completo de IA para Suporte Emocional - Versão Modular
Inclui: Análise de Sentimentos, Geração de Respostas, RAG e Sistema de Prompts

"""

import json
import os
import logging
import random
from datetime import datetime, UTC
from typing import Dict, List, Optional
from sqlalchemy import text

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# === DEPENDÊNCIAS OPCIONAIS ===
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


# === IMPORTAR SISTEMA DE PROMPTS CONSOLIDADO ===
from .ai_prompt import AIPromptManager, PromptContext, RiskLevel, PromptType

# === IMPORTAR SISTEMAS AVANÇADOS ===
from .finetuning_preparator import finetuning_preparator

# Configurar logging
logger = logging.getLogger(__name__)


class SimpleRAG:
    """
    Sistema RAG (Retrieval-Augmented Generation) Completo e Consolidado
    
    Funcionalidades:
    - Busca conversas similares bem-sucedidas no banco
    - Extração inteligente de palavras-chave
    - Ranking por relevância com múltiplos fatores
    - Busca em dados de treinamento
    - Context enhancement para diferentes tipos de consulta
    - Cache para otimização de performance
    - Sistema unificado (substitui advanced_rag_service)
    """
    
    def __init__(self):
        """Inicializa o sistema RAG consolidado"""
        self.cache = {}  # Cache simples mas eficaz
        self.training_cache = {}  # Cache para dados de treinamento
        logger.info("SimpleRAG consolidado inicializado")
    
    def get_relevant_context(self, user_message: str, risk_level: str = 'low', 
                           limit: int = 3) -> Optional[str]:
        print(f"[RAG] Buscando contexto para: '{user_message}' | Risco: {risk_level} | Limite: {limit}")
        """
        Busca contexto relevante de conversas bem-sucedidas
        
        Args:
            user_message: Mensagem do usuário
            risk_level: Nível de risco (low, moderate, high, critical)
            limit: Número máximo de exemplos a retornar
            
        Returns:
            String com contexto relevante ou None se não encontrar
        """
        try:
            # Verificar cache primeiro
            cache_key = f"{hash(user_message)}_{risk_level}_{limit}"
            if cache_key in self.cache:
                print(f"[RAG] Contexto encontrado no cache.")
                return self.cache[cache_key]

            # Extrair palavras-chave da mensagem
            keywords = self._extract_keywords(user_message)
            print(f"[RAG] Palavras-chave extraídas: {keywords}")

            # Buscar conversas similares
            similar_conversations = self._find_similar_conversations(keywords, risk_level, limit * 2)
            print(f"[RAG] Conversas similares encontradas: {len(similar_conversations)}")

            # Ranquear por relevância
            ranked_conversations = self._rank_conversations(similar_conversations, user_message)
            print(f"[RAG] Conversas ranqueadas: {len(ranked_conversations)}")

            # Construir contexto a partir das melhores
            context = self._build_context(ranked_conversations[:limit])
            print(f"[RAG] Contexto final gerado: {'Sim' if context else 'Não'}")

            # Cachear resultado
            self.cache[cache_key] = context

            return context

        except Exception as e:
            logger.error(f"Erro no RAG: {e}")
            print(f"[RAG] Erro: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave relevantes para saúde mental"""
        mental_health_keywords = [
            'ansiedade', 'depressão', 'tristeza', 'medo', 'preocupação',
            'estresse', 'pânico', 'angústia', 'solidão', 'vazio', 'raiva',
            'trabalho', 'família', 'relacionamento', 'escola', 'faculdade',
            'dinheiro', 'saúde', 'futuro', 'passado', 'culpa', 'frustração'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        # Buscar palavras-chave específicas
        for keyword in mental_health_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Adicionar palavras importantes do texto (> 4 caracteres)
        words = [w for w in text_lower.split() if len(w) > 4 and w.isalpha()]
        found_keywords.extend(words[:5])
        
        return list(set(found_keywords))[:10]  # Remover duplicatas e limitar
    
    def _find_similar_conversations(self, keywords: List[str], risk_level: str, 
                                  limit: int = 10) -> List[Dict]:
        print(f"[RAG] Buscando conversas no banco. Keywords: {keywords} | Limite: {limit}")
        """Busca conversas similares no banco de dados priorizando só palavras-chave e avaliação, sem filtrar por risco"""
        try:
            from app import db
            if keywords:
                keyword_pattern = '|'.join([k for k in keywords if len(k) > 3])
            else:
                keyword_pattern = ''
            # 1. Busca com keywords (qualquer risco)
            query = text("""
                SELECT DISTINCT
                    cm_user.content as user_message,
                    cm_ai.content as ai_response,
                    cs.user_rating,
                    cs.initial_risk_level,
                    cm_ai.created_at
                FROM chat_sessions cs
                JOIN chat_messages cm_user ON cs.id = cm_user.session_id 
                    AND cm_user.message_type = 'USER'
                JOIN chat_messages cm_ai ON cs.id = cm_ai.session_id 
                    AND cm_ai.message_type = 'AI'
                    AND cm_ai.id > cm_user.id
                WHERE 
                    cs.user_rating >= 4
                    AND (:keyword_pattern = '' OR cm_user.content ~* :keyword_pattern)
                    AND cm_user.created_at >= NOW() - INTERVAL '6 months'
                    AND LENGTH(cm_user.content) > 10
                    AND LENGTH(cm_ai.content) > 20
                ORDER BY cs.user_rating DESC, cm_ai.created_at DESC
                LIMIT :limit
            """)
            result = db.session.execute(query, {
                'keyword_pattern': keyword_pattern,
                'limit': limit
            })
            rows = [dict(row._mapping) for row in result]
            print(f"[RAG] Linhas retornadas do banco (keywords): {len(rows)}")
            if rows:
                return rows
            # 2. Última tentativa: pega os últimos registros bem avaliados
            query = text("""
                SELECT DISTINCT
                    cm_user.content as user_message,
                    cm_ai.content as ai_response,
                    cs.user_rating,
                    cs.initial_risk_level,
                    cm_ai.created_at
                FROM chat_sessions cs
                JOIN chat_messages cm_user ON cs.id = cm_user.session_id 
                    AND cm_user.message_type = 'USER'
                JOIN chat_messages cm_ai ON cs.id = cm_ai.session_id 
                    AND cm_ai.message_type = 'AI'
                    AND cm_ai.id > cm_user.id
                WHERE 
                    cs.user_rating >= 4
                    AND cm_user.created_at >= NOW() - INTERVAL '6 months'
                    AND LENGTH(cm_user.content) > 10
                    AND LENGTH(cm_ai.content) > 20
                ORDER BY cs.user_rating DESC, cm_ai.created_at DESC
                LIMIT :limit
            """)
            result = db.session.execute(query, {
                'limit': limit
            })
            rows = [dict(row._mapping) for row in result]
            print(f"[RAG] Linhas retornadas do banco (só últimos): {len(rows)}")
            return rows
        except Exception as e:
            logger.error(f"Erro na busca de conversas: {e}")
            print(f"[RAG] Erro: {e}")
            return []
    
    def _rank_conversations(self, conversations: List[Dict], user_message: str) -> List[Dict]:
        """Ranqueia conversas por relevância"""
        if not conversations:
            return []
        
        user_words = set(user_message.lower().split())
        
        for conv in conversations:
            try:
                conv_words = set(conv['user_message'].lower().split())
                common_words = len(user_words.intersection(conv_words))
                word_similarity = common_words / max(len(user_words), 1)
                rating_score = (conv.get('user_rating', 3)) / 5.0
                
                # Score final ponderado
                conv['relevance_score'] = (word_similarity * 0.6) + (rating_score * 0.4)
                
            except Exception:
                conv['relevance_score'] = 0
        
        conversations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return conversations
    
    def _build_context(self, conversations: List[Dict]) -> Optional[str]:
        """Constrói contexto formatado a partir das melhores conversas"""
        if not conversations:
            return None
        
        context_parts = ["EXEMPLOS DE RESPOSTAS EFICAZES:\n"]
        
        for i, conv in enumerate(conversations, 1):
            user_msg = conv['user_message'][:120]
            ai_response = conv['ai_response'][:200]
            rating = conv.get('user_rating', 0)
            
            context_parts.append(
                f"Exemplo {i} (⭐{rating}/5):\n"
                f"Situação: {user_msg}{'...' if len(conv['user_message']) > 120 else ''}\n"
                f"Resposta eficaz: {ai_response}{'...' if len(conv['ai_response']) > 200 else ''}\n"
            )
        
        context_parts.append("\n💡 Use como inspiração, mas personalize para o contexto atual.")
        return "\n".join(context_parts)
    
    # === MÉTODOS AVANÇADOS (CONSOLIDADOS DO ADVANCED RAG SERVICE) ===
    
    def get_enhanced_context(self, user_message: str, risk_level: str, 
                           context_type: str = 'all', limit: int = 3) -> Dict:
        """
        Método avançado para buscar contexto enriquecido
        
        Args:
            user_message: Mensagem do usuário
            risk_level: Nível de risco
            context_type: Tipo de contexto ('all', 'conversations', 'training')
            limit: Limite de resultados
            
        Returns:
            Dict com contexto_prompt, training_data e conversation_examples
        """
        try:
            result = {
                'context_prompt': '',
                'training_data': [],
                'conversation_examples': []
            }
            
            # Buscar conversas se solicitado
            if context_type in ['all', 'conversations']:
                conversation_context = self.get_relevant_context(user_message, risk_level, limit)
                if conversation_context:
                    result['context_prompt'] += conversation_context
                    result['conversation_examples'] = self._get_conversation_examples(user_message, risk_level, limit)
            
            # Buscar dados de treinamento se solicitado
            if context_type in ['all', 'training']:
                training_context = self._get_training_context(user_message, risk_level, limit)
                if training_context:
                    result['context_prompt'] += f"\n\n{training_context}"
                    result['training_data'] = self._get_training_data_details(user_message, limit)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no enhanced context: {e}")
            return {'context_prompt': '', 'training_data': [], 'conversation_examples': []}
    
    def search_training_content(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Busca conteúdo de treinamento baseado na query
        
        Args:
            query: Consulta de busca
            limit: Limite de resultados
            
        Returns:
            Lista de dicionários com conteúdo encontrado
        """
        try:
            cache_key = f"training_search_{hash(query)}_{limit}"
            if cache_key in self.training_cache:
                return self.training_cache[cache_key]
            
            # Implementação simples de busca em training data
            # Aqui você pode expandir para buscar em diferentes fontes
            keywords = self._extract_keywords(query)
            
            # Buscar em sessões de alta qualidade como "dados de treinamento"
            training_results = self._find_training_like_content(keywords, limit)
            
            self.training_cache[cache_key] = training_results
            return training_results
            
        except Exception as e:
            logger.error(f"Erro na busca de training content: {e}")
            return []
    
    def get_training_data_statistics(self) -> Dict:
        """
        Retorna estatísticas dos dados de treinamento/RAG
        
        Returns:
            Dict com estatísticas do sistema
        """
        try:
            from app import db
            
            # Estatísticas de conversas bem-sucedidas
            conv_stats_query = text("""
                SELECT 
                    COUNT(*) as total_sessions,
                    AVG(user_rating) as avg_rating,
                    COUNT(CASE WHEN user_rating >= 4 THEN 1 END) as high_quality_sessions
                FROM chat_sessions 
                WHERE user_rating IS NOT NULL
                    AND created_at >= NOW() - INTERVAL '6 months'
            """)
            
            result = db.session.execute(conv_stats_query).first()
            
            return {
                'total_conversations': int(result.total_sessions) if result else 0,
                'average_rating': float(result.avg_rating) if result and result.avg_rating else 0,
                'high_quality_conversations': int(result.high_quality_sessions) if result else 0,
                'cache_size': len(self.cache),
                'training_cache_size': len(self.training_cache),
                'system_type': 'consolidated_rag'
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_conversations': 0,
                'average_rating': 0,
                'high_quality_conversations': 0,
                'cache_size': len(self.cache),
                'training_cache_size': len(self.training_cache),
                'system_type': 'consolidated_rag',
                'error': str(e)
            }
    
    def _get_conversation_examples(self, user_message: str, risk_level: str, limit: int) -> List[Dict]:
        print(f"[RAG] Obtendo exemplos de conversas para: '{user_message}' | Risco: {risk_level} | Limite: {limit}")
        """Obtém exemplos de conversas formatados para o sistema de prompts"""
        try:
            conversations = self._find_similar_conversations(
                self._extract_keywords(user_message), 
                risk_level, 
                limit
            )
            
            examples = []
            for conv in conversations[:limit]:
                examples.append({
                    'user_message': conv['user_message'],
                    'ai_response': conv['ai_response'],
                    'rating': conv.get('user_rating', 3),
                    'risk_level': conv.get('initial_risk_level', 'moderate')
                })
            
            print(f"[RAG] Exemplos de conversas retornados: {len(examples)}")
            return examples
            
        except Exception as e:
            logger.error(f"Erro ao obter exemplos: {e}")
            return []
    
    def _get_training_context(self, user_message: str, risk_level: str, limit: int) -> Optional[str]:
        """Constrói contexto baseado em dados de treinamento"""
        try:
            training_data = self.search_training_content(user_message, limit)
            
            if not training_data:
                return None
            
            context_parts = ["CONHECIMENTO DE TREINAMENTO RELEVANTE:\n"]
            
            for i, item in enumerate(training_data, 1):
                context_parts.append(
                    f"Situação {i}: {item.get('situation', '')}[:150]\n"
                    f"Abordagem recomendada: {item.get('approach', '')}[:200]\n"
                )
            
            context_parts.append("\n💡 Aplique este conhecimento ao contexto específico do usuário.")
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Erro no contexto de treinamento: {e}")
            return None
    
    def _get_training_data_details(self, user_message: str, limit: int) -> List[Dict]:
        """Obtém detalhes dos dados de treinamento para contexto avançado"""
        return self.search_training_content(user_message, limit)
    
    def _find_training_like_content(self, keywords: List[str], limit: int) -> List[Dict]:
        """
        Busca conteúdo que pode servir como dados de treinamento
        (conversas de alta qualidade, casos bem documentados, etc.)
        """
        try:
            from app import db
            
            if keywords:
                keyword_pattern = '|'.join([k for k in keywords if len(k) > 3])
            else:
                keyword_pattern = ''
            
            # Buscar conversas muito bem avaliadas como "dados de treinamento"
            query = text("""
                SELECT 
                    cm_user.content as situation,
                    cm_ai.content as approach,
                    cs.user_rating,
                    cs.initial_risk_level,
                    'high_quality_conversation' as source_type
                FROM chat_sessions cs
                JOIN chat_messages cm_user ON cs.id = cm_user.session_id 
                    AND cm_user.message_type = 'USER'
                JOIN chat_messages cm_ai ON cs.id = cm_ai.session_id 
                    AND cm_ai.message_type = 'AI'
                    AND cm_ai.id > cm_user.id
                WHERE 
                    cs.user_rating = 5  -- Apenas conversas perfeitas
                    AND (:keyword_pattern = '' OR cm_user.content ~* :keyword_pattern)
                    AND LENGTH(cm_user.content) > 15
                    AND LENGTH(cm_ai.content) > 30
                ORDER BY cs.created_at DESC
                LIMIT :limit
            """)
            
            result = db.session.execute(query, {
                'keyword_pattern': keyword_pattern,
                'limit': limit
            })
            
            return [dict(row._mapping) for row in result]
            
        except Exception as e:
            logger.error(f"Erro na busca de training-like content: {e}")
            return []


class AIService:
    """
    Serviço Completo de IA para Suporte Emocional
    
    Funcionalidades principais:
    - Análise de sentimentos com OpenAI
    - Avaliação de níveis de risco integrada
    - Geração de respostas empáticas contextualizadas  
    - Sistema RAG para melhor qualidade
    - Sistema de prompts modular e manutenível
    - Fallback para múltiplos modelos
    - Cache e otimizações de performance
    
    Versão: 2.1 - Modular com Prompt Manager Separado
    """
    
    def __init__(self, app=None):
        """
        Inicializa o serviço de IA com todas as funcionalidades
        
        Args:
            app: Instância da aplicação Flask (opcional)
        """
        self.app = app
        
        # === CONFIGURAÇÃO OPENAI (Principal) ===
        self.openai_client = None
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 300))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.5))
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = openai
            self.openai_client.api_key = openai_api_key
            print(f"[INFO] OpenAI configurado | Modelo: {self.openai_model} | Temperatura: {self.temperature}")
        else:
            logger.warning("OpenAI API key não encontrada")
        
        # === CONFIGURAÇÃO GEMINI (Fallback) ===
        self.gemini_client = None
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        
        if GEMINI_AVAILABLE:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                try:
                    genai.configure(api_key=gemini_api_key)
                    self.gemini_client = genai
                    logger.info("Gemini configurado como fallback")
                except Exception as e:
                    logger.error(f"Erro ao configurar Gemini: {e}")
        

        
        # === SISTEMA RAG CONSOLIDADO ===
        self.rag = SimpleRAG()  # Sistema RAG unificado e completo
        self.rag_enabled = True
        # Alias para compatibilidade - aponta para o mesmo sistema consolidado
        self.advanced_rag = self.rag
        
        # === SISTEMA DE PROMPTS CONSOLIDADO ===
        self.prompt_manager = AIPromptManager()  # Sistema unificado de prompts
        
        # === SISTEMA DE FINE-TUNING ===
        self.finetuning_preparator = finetuning_preparator
        
        # === SISTEMA DE LOGGING DE TREINAMENTO ===
        self.log_training_usage = False  # Desabilitado - logger não disponível
        
        # === CACHE E OTIMIZAÇÕES ===
        self.response_cache = {}
        self.cache_max_size = 100
        
        logger.info("AIService v2.0 inicializado com sucesso")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analisa o sentimento do texto usando OpenAI com fallback inteligente
        Garante que o prompt peça resposta JSON, faz print do retorno e trata erro de parsing.
        """
        if not self.openai_client:
            return self._basic_sentiment_analysis(text)

        try:
            # Prompt explícito para resposta JSON
            system_content = (
                "Você é um analisador de sentimentos. Analise a mensagem do usuário e responda estritamente neste formato JSON: "
                '{"score": float, "confidence": float, "emotion": "...", "intensity": "..."}'
                "\nNão adicione explicações, apenas o JSON."
            )
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": f"Mensagem: {text}"}
                ],
                max_tokens=150,
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()
            print(f"[OpenAI Sentiment Raw]: {content}")
            try:
                result = json.loads(content)
            except Exception as e:
                logger.error(f"Erro ao fazer parse do JSON retornado pela OpenAI: {e} | Conteúdo: {content}")
                return self._basic_sentiment_analysis(text)

            # Validar resultado
            if all(key in result for key in ['score', 'confidence', 'emotion', 'intensity']):
                return result
            else:
                return self._basic_sentiment_analysis(text)

        except Exception as e:
            logger.error(f"Erro na análise OpenAI: {e}")
            return self._basic_sentiment_analysis(text)
    
    def _basic_sentiment_analysis(self, text: str) -> Dict:
        """Análise básica de sentimento como fallback"""
        text_lower = text.lower()
        
        positive_words = ['bem', 'bom', 'feliz', 'alegre', 'ótimo', 'amor', 'paz']
        negative_words = ['mal', 'ruim', 'triste', 'deprimido', 'ódio', 'raiva', 'medo']
        critical_words = ['morrer', 'matar', 'suicídio', 'acabar', 'desistir']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        critical_count = sum(1 for word in critical_words if word in text_lower)
        
        total_words = max(len(text_lower.split()), 1)
        score = (positive_count - negative_count - critical_count * 2) / total_words
        score = max(-1, min(1, score))
        
        if critical_count > 0:
            emotion, intensity = 'desesperado', 'high'
        elif score < -0.3:
            emotion = 'triste'
            intensity = 'high' if score < -0.6 else 'moderate'
        elif score > 0.3:
            emotion, intensity = 'feliz', 'moderate'
        else:
            emotion, intensity = 'neutro', 'low'
        
        return {
            'score': score,
            'confidence': 0.6,
            'emotion': emotion,
            'intensity': intensity
        }
    
    def assess_risk_level(self, text: str, sentiment_analysis: Optional[Dict] = None) -> str:
        """
        Avalia nível de risco usando RiskAnalyzer integrado
        
        Args:
            text: Texto para análise
            sentiment_analysis: Análise de sentimento prévia (opcional)
            
        Returns:
            Nível de risco: 'low', 'moderate', 'high', 'critical'
        """
        try:
            from app.services.risk_analyzer import RiskAnalyzer
            risk_analyzer = RiskAnalyzer()
            analysis = risk_analyzer.analyze_message(text)
            return analysis.get('risk_level', 'low')
        except ImportError:
            logger.warning("RiskAnalyzer não disponível, usando análise básica")
            return self._basic_risk_assessment(text, sentiment_analysis)
    
    def _basic_risk_assessment(self, text: str, sentiment_analysis: Optional[Dict] = None) -> str:
        """Avaliação básica de risco como fallback, com prints de debug"""
        text_lower = text.lower()

        critical_keywords = [
            'me matar', 'suicídio', 'quero morrer', 'acabar com tudo',
            'não quero viver', 'melhor morto',
            # Frases indiretas de ideação suicida
            'não ta fazendo muito sentido ficar aqui',
            'não faz sentido continuar',
            'não vejo mais sentido',
            'não quero mais estar aqui',
            'preferia não existir',
            'não aguento mais viver',
            'cansei de tudo',
            'não vejo saída',
            'não vejo esperança',
            'não vejo motivo pra continuar'
        ]

        high_keywords = [
            'não aguento mais', 'desesperado', 'sem esperança', 'vazio total',
            'depressão severa', 'ansiedade extrema'
        ]

        moderate_keywords = [
            'triste', 'ansioso', 'preocupado', 'difícil', 'problema', 'ajuda'
        ]

        found_critical = [k for k in critical_keywords if k in text_lower]
        found_high = [k for k in high_keywords if k in text_lower]
        found_moderate = [k for k in moderate_keywords if k in text_lower]

        print(f"[RISK DEBUG] Texto: '{text}'")
        print(f"[RISK DEBUG] Palavras críticas encontradas: {found_critical}")
        print(f"[RISK DEBUG] Palavras high encontradas: {found_high}")
        print(f"[RISK DEBUG] Palavras moderate encontradas: {found_moderate}")

        # Verificar palavras críticas e frases indiretas
        if found_critical:
            print("[RISK DEBUG] Risco atribuído: critical (palavra crítica)")
            return 'critical'

        # Usar análise de sentimento se disponível
        if sentiment_analysis:
            score = sentiment_analysis.get('score', 0)
            emotion = sentiment_analysis.get('emotion', '')
            print(f"[RISK DEBUG] Análise de sentimento: score={score}, emotion={emotion}")
            if emotion == 'desesperado' or score < -0.8:
                print("[RISK DEBUG] Risco atribuído: critical (sentimento)")
                return 'critical'
            elif score < -0.5:
                print("[RISK DEBUG] Risco atribuído: high (sentimento)")
                return 'high'

        # Verificar outras palavras-chave
        if found_high:
            print("[RISK DEBUG] Risco atribuído: high (palavra high)")
            return 'high'

        if found_moderate:
            print("[RISK DEBUG] Risco atribuído: moderate (palavra moderate)")
            return 'moderate'

        print("[RISK DEBUG] Risco atribuído: low (nenhum match)")
        return 'low'
        
        # Verificar palavras críticas
        for keyword in critical_keywords:
            if keyword in text_lower:
                return 'critical'
        
        # Usar análise de sentimento se disponível
        if sentiment_analysis:
            score = sentiment_analysis.get('score', 0)
            emotion = sentiment_analysis.get('emotion', '').lower()
            intensity = sentiment_analysis.get('intensity', '').lower()
            
            if emotion == 'desesperado' and intensity == 'high':
                return 'critical'
            elif emotion in ['triste', 'vazio'] and intensity == 'high' and score < -0.7:
                return 'high'
        
        # Verificar outras palavras-chave
        for keyword in high_keywords:
            if keyword in text_lower:
                return 'high'
        
        for keyword in moderate_keywords:
            if keyword in text_lower:
                return 'moderate'
        
        return 'low'
    
    def analyze_with_risk_assessment(self, text: str) -> Dict:
        """
        Análise completa: sentimento + risco em uma chamada otimizada
        
        Args:
            text: Texto para análise completa
            
        Returns:
            Dict com análise completa
        """
        try:
            # Verificar cache primeiro
            cache_key = f"analysis_{hash(text)}"
            if cache_key in self.response_cache:
                return self.response_cache[cache_key]
            
            # Análise de sentimento
            sentiment_result = self.analyze_sentiment(text)
            
            # Avaliação de risco
            risk_level = self.assess_risk_level(text, sentiment_result)
            
            # Combinar resultados
            sentiment_result.update({
                'risk_level': risk_level,
                'requires_attention': risk_level in ['high', 'critical'],
                'timestamp': datetime.now(UTC).isoformat()
            })
            
            # Cachear resultado
            self._cache_result(cache_key, sentiment_result)
            
            return sentiment_result
            
        except Exception as e:
            logger.error(f"Erro na análise completa: {e}")
            return {
                'score': 0,
                'confidence': 0.1,
                'emotion': 'neutro',
                'intensity': 'low',
                'risk_level': self.assess_risk_level(text),
                'requires_attention': False,
                'error': str(e),
                'timestamp': datetime.now(UTC).isoformat()
            }
    
    def analyze_diary_entry(self, entry_content: str) -> Optional[Dict]:
        """
        Analisa uma entrada do diário para extrair insights emocionais
        
        Args:
            entry_content: Conteúdo da entrada do diário
            
        Returns:
            Dict com análise da entrada ou None em caso de erro
        """
        try:
            if not entry_content or not entry_content.strip():
                return None
            
            # Análise de sentimento básica
            sentiment_result = self.analyze_sentiment(entry_content)
            
            # Detectar emoções específicas usando palavras-chave
            emotions = self._detect_emotions_in_text(entry_content)
            
            # Identificar indicadores de risco
            risk_indicators = self._identify_risk_indicators(entry_content)
            
            # Extrair temas principais
            themes = self._extract_themes(entry_content)
            
            # Compilar análise completa
            analysis = {
                'sentiment_score': sentiment_result.get('score', 0),
                'primary_emotion': sentiment_result.get('emotion', 'neutro'),
                'emotional_intensity': sentiment_result.get('intensity', 'low'),
                'detected_emotions': emotions,
                'risk_indicators': risk_indicators,
                'main_themes': themes,
                'analysis_timestamp': datetime.now(UTC).isoformat(),
                'word_count': len(entry_content.split()),
                'requires_attention': len(risk_indicators) > 0 or sentiment_result.get('score', 0) < -0.6
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise do diário: {e}")
            return None
    
    def _detect_emotions_in_text(self, text: str) -> List[str]:
        """Detecta emoções específicas no texto usando palavras-chave"""
        emotion_keywords = {
            'alegria': ['feliz', 'alegre', 'contente', 'animado', 'eufórico', 'radiante', 'otimista'],
            'tristeza': ['triste', 'melancólico', 'deprimido', 'abatido', 'desanimado', 'lamentando'],
            'ansiedade': ['ansioso', 'nervoso', 'preocupado', 'inquieto', 'apreensivo', 'tenso'],
            'raiva': ['raiva', 'irritado', 'furioso', 'bravo', 'indignado', 'revoltado'],
            'medo': ['medo', 'amedrontado', 'assustado', 'aterrorizado', 'receoso'],
            'gratidão': ['grato', 'agradecido', 'reconhecido', 'abençoado'],
            'amor': ['amor', 'carinho', 'afeto', 'paixão', 'adoração'],
            'esperança': ['esperança', 'esperançoso', 'confiante', 'positivo'],
            'solidão': ['sozinho', 'isolado', 'abandonado', 'solitário'],
            'culpa': ['culpa', 'culpado', 'arrependido', 'remorso']
        }
        
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions[:3]  # Máximo 3 emoções principais
    
    def _identify_risk_indicators(self, text: str) -> List[str]:
        """Identifica indicadores de risco no texto"""
        risk_keywords = {
            'suicidal_ideation': ['suicídio', 'acabar com tudo', 'não aguento mais', 'quero morrer'],
            'self_harm': ['me machucar', 'me cortar', 'autolesão', 'me ferir'],
            'substance_abuse': ['bebendo muito', 'usando drogas', 'viciado', 'dependente'],
            'eating_disorder': ['não como', 'vomito', 'bulimia', 'anorexia'],
            'severe_depression': ['não vejo sentido', 'vida sem propósito', 'desesperança total'],
            'panic_attacks': ['pânico', 'coração acelerado', 'não consigo respirar', 'ataque'],
            'social_isolation': ['não saio', 'evito pessoas', 'me isolo', 'ninguém me entende']
        }
        
        text_lower = text.lower()
        risk_indicators = []
        
        for risk_type, keywords in risk_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                risk_indicators.append(risk_type)
        
        return risk_indicators
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extrai temas principais do texto"""
        theme_keywords = {
            'trabalho': ['trabalho', 'emprego', 'chefe', 'colega', 'carreira', 'profissional'],
            'família': ['família', 'pai', 'mãe', 'irmão', 'filho', 'parente'],
            'relacionamento': ['namorado', 'namorada', 'marido', 'esposa', 'relacionamento', 'amor'],
            'estudos': ['escola', 'universidade', 'faculdade', 'estudo', 'prova', 'professor'],
            'saúde': ['saúde', 'doença', 'médico', 'hospital', 'tratamento', 'dor'],
            'finanças': ['dinheiro', 'financeiro', 'conta', 'pagamento', 'dívida', 'salário'],
            'amizade': ['amigo', 'amiga', 'amizade', 'colega', 'turma'],
            'futuro': ['futuro', 'planos', 'objetivos', 'sonhos', 'metas', 'amanhã'],
            'autoestima': ['autoestima', 'confiança', 'inseguro', 'valor próprio', 'autoimagem']
        }
        
        text_lower = text.lower()
        themes = []
        
        for theme, keywords in theme_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_count >= 2:  # Pelo menos 2 palavras-chave do tema
                themes.append(theme)
            elif keyword_count == 1 and len([k for k in keywords if k in text_lower and len(k) > 6]) > 0:
                # Uma palavra-chave específica/longa
                themes.append(theme)
        
        return themes[:5]  # Máximo 5 temas
    
    def generate_response(self, user_message: str, risk_level: str = 'low', 
                         user_context: Optional[Dict] = None, 
                         conversation_history: Optional[List] = None, 
                         fallback: bool = True) -> Dict:
        """
        Gera resposta empática usando LLMs com RAG avançado e Prompt Engineering
        
        Args:
            user_message: Mensagem do usuário
            risk_level: Nível de risco detectado
            user_context: Contexto do usuário (nome, etc.)
            conversation_history: Histórico da conversa
            fallback: Se deve usar fallback em caso de erro
            
        Returns:
            Dict com resposta gerada e metadados
        """
        errors = []

        # RESPOSTAS INTELIGENTES SOBRE O HISTÓRICO E CONTEXTO COMPLETO
        user_message_lower = user_message.lower()


        errors = []
        
        try:
            print(f"AI_RESPONSE_START: Processando mensagem de risco {risk_level}")
            
            # 1. Buscar contexto avançado usando RAG
            rag_context = None
            rag_result = None
            if self.rag_enabled:
                try:
                    rag_result = self.rag.get_enhanced_context(
                        user_message, 
                        risk_level, 
                        context_type='all', 
                        limit=3
                    )
                    rag_context = rag_result.get('context_prompt', '')
                    print(f"RAG_CONTEXT: {len(rag_result.get('training_data', []))} dados + {len(rag_result.get('conversation_examples', []))} conversas")
                except Exception as e:
                    logger.warning(f"Erro no RAG: {e}")

            # 2. Preparar contexto para prompt engineering (incluindo triagem)
            prompt_context = PromptContext(
                user_message=user_message,
                risk_level=RiskLevel(risk_level),
                user_name=user_context.get('name') if user_context else None,
                session_history=conversation_history,
                training_context=rag_context,
                conversation_examples=rag_result.get('conversation_examples', []) if rag_result else None
            )


            # 2.1. Adicionar contexto de triagem se disponível
            if user_context:
                triage_triggered = user_context.get('triage_triggered', False)
                triage_status = user_context.get('triage_status')
                triage_declined_reason = user_context.get('triage_declined_reason')

                # Construir contexto de triagem para a IA
                triage_context_info = ""
                triage_print_reason = None
                if triage_triggered:
                    if triage_status == 'declined':
                        triage_context_info = f"\n\nCONTEXTO IMPORTANTE: O usuário recusou participar da triagem psicológica. "
                        if triage_declined_reason:
                            triage_context_info += f"Motivo: {triage_declined_reason}. "
                            triage_print_reason = f"Usuário recusou triagem. Motivo: {triage_declined_reason}"
                        else:
                            triage_print_reason = "Usuário recusou triagem. Sem motivo informado."
                        triage_context_info += "Seja respeitoso com essa decisão, mas mantenha-se atento aos sinais de risco. Não insista na triagem, mas continue oferecendo apoio emocional."
                    elif triage_status == 'initiated':
                        triage_context_info = f"\n\nCONTEXTO: O usuário iniciou o processo de triagem psicológica. Apoie e encoraje a continuidade deste processo."
                        triage_print_reason = "Usuário iniciou a triagem psicológica."
                    elif triage_status == 'completed':
                        triage_context_info = f"\n\nCONTEXTO: O usuário completou a triagem psicológica. Use essas informações para personalizar melhor suas respostas."
                        triage_print_reason = "Usuário completou a triagem psicológica."

                # Adicionar ao contexto de treinamento
                if triage_context_info and prompt_context.training_context:
                    prompt_context.training_context += triage_context_info
                elif triage_context_info:
                    prompt_context.training_context = triage_context_info

                # Print informativo
                if triage_print_reason:
                    print(f"[TRIAGEM ATIVADA] Status: {triage_status} | Motivo: {triage_print_reason}")

            # 3. Tentar OpenAI consolidado
            if self.openai_client:
                try:
                    prompt_data = self.prompt_manager.build_contextual_prompt(prompt_context, provider='openai')
                    response = self.openai_client.chat.completions.create(
                        model=self.openai_model,
                        messages=prompt_data['messages'],
                        max_tokens=prompt_data.get('max_tokens', 120),
                        temperature=prompt_data.get('temperature', 0.7),
                        presence_penalty=prompt_data.get('presence_penalty', 0),
                        frequency_penalty=prompt_data.get('frequency_penalty', 0)
                    )
                    ai_response = response.choices[0].message.content.strip()
                    result = {
                        'message': ai_response,
                        'risk_level': prompt_context.risk_level.value,
                        'confidence': 0.95,
                        'source': 'openai',
                        'model': self.openai_model,
                        'rag_used': bool(prompt_context.training_context),
                        'prompt_engineering': 'consolidated',
                        'timestamp': datetime.now(UTC).isoformat(),
                        'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
                    }
                    if prompt_context.training_context:
                        result['rag_context_length'] = len(prompt_context.training_context)
                    return result
                except Exception as e:
                    errors.append(f"OpenAI: {str(e)}")
                    logger.warning(f"Falha no OpenAI: {e}")

            # 4. Tentar Gemini consolidado (fallback)
            if self.gemini_client and fallback:
                try:
                    prompt_data = self.prompt_manager.build_contextual_prompt(prompt_context, provider='gemini')
                    model = self.gemini_client.GenerativeModel(self.gemini_model)
                    response = model.generate_content(prompt_data['prompt'])
                    ai_response = response.text.strip()
                    result = {
                        'message': ai_response,
                        'risk_level': prompt_context.risk_level.value,
                        'confidence': 0.90,
                        'source': 'gemini',
                        'rag_used': bool(prompt_context.training_context),
                        'prompt_engineering': 'consolidated',
                        'timestamp': datetime.now(UTC).isoformat()
                    }
                    if prompt_context.training_context:
                        result['rag_context_length'] = len(prompt_context.training_context)
                    return result
                except Exception as e:
                    errors.append(f"Gemini: {str(e)}")
                    logger.warning(f"Falha no Gemini: {e}")

            # 5. Fallback para resposta estática
            return self._generate_response_fallback(user_message, risk_level, user_context, errors)
            
        except Exception as e:
            logger.error(f"Erro crítico na geração de resposta: {e}")
            return self._generate_response_fallback(user_message, risk_level, user_context, errors + [str(e)])
    
    
    def _generate_response_fallback(self, user_message: str, risk_level: str, 
                                   user_context: Optional[Dict], 
                                   errors: Optional[List] = None) -> Dict:
        """Gera resposta estática como fallback final"""
        
        # Obter respostas do sistema de prompts
        responses = self.prompt_manager.get_fallback_responses(risk_level, user_context)
        message = random.choice(responses)
        
        return {
            'message': message,
            'risk_level': risk_level,
            'confidence': 0.3,
            'source': 'fallback',
            'errors': errors or [],
            'timestamp': datetime.now(UTC).isoformat()
        }
    
    def _cache_result(self, key: str, result: Dict) -> None:
        """Gerencia cache com limpeza automática"""
        try:
            if len(self.response_cache) >= self.cache_max_size:
                # Remove primeiros 20% dos itens
                items_to_remove = list(self.response_cache.keys())[:self.cache_max_size // 5]
                for item_key in items_to_remove:
                    del self.response_cache[item_key]
            
            self.response_cache[key] = result
        except Exception as e:
            logger.warning(f"Erro ao cachear: {e}")
    
    def get_model_info(self) -> List[Dict]:
        """Retorna informações sobre modelos configurados"""
        return [
            {
                'provider': 'OpenAI',
                'model': self.openai_model,
                'status': 'active' if self.openai_client else 'inactive',
                'type': 'cloud',
                'primary': True
            },
            {
                'provider': 'Gemini',
                'model': self.gemini_model,
                'status': 'active' if self.gemini_client else 'inactive',
                'type': 'cloud',
                'primary': False
            },
            {
                'provider': 'RAG',
                'model': 'SimpleRAG',
                'status': 'active' if self.rag_enabled else 'inactive',
                'type': 'enhancement',
                'primary': False
            },
            {
                'provider': 'PromptManager',
                'model': 'AIPromptManager',
                'status': 'active',
                'type': 'prompt_system',
                'primary': False
            },
            {
                'provider': 'Fallback',
                'model': 'static_responses',
                'status': 'always',
                'type': 'static',
                'primary': False
            }
        ]
    
    def get_service_statistics(self) -> Dict:
        """Retorna estatísticas do serviço"""
        try:
            stats = {
                'service_version': '3.0',
                'architecture': 'advanced_integrated_system',
                'models_active': len([m for m in self.get_model_info() if m['status'] == 'active']),
                'cache_size': len(self.response_cache),
                'rag_enabled': self.rag_enabled,
                'prompt_manager_active': bool(self.prompt_manager),
                'training_logging_enabled': self.log_training_usage,
                'advanced_systems': {
                    'advanced_rag': bool(self.advanced_rag),
                    'consolidated_prompt_manager': bool(self.prompt_manager),
                    'finetuning_preparator': bool(self.finetuning_preparator)
                }
            }
            
            # Estatísticas do RAG avançado
            if self.advanced_rag:
                try:
                    rag_stats = self.advanced_rag.get_training_data_statistics()
                    stats['advanced_rag_stats'] = rag_stats
                except Exception as e:
                    stats['advanced_rag_error'] = str(e)
            
            # Estatísticas do sistema consolidado de prompts
            if self.prompt_manager:
                try:
                    prompt_stats = self.prompt_manager.get_prompt_statistics()
                    stats['prompt_engineering_stats'] = prompt_stats
                except Exception as e:
                    stats['prompt_engineering_error'] = str(e)
            
            # Estatísticas do fine-tuning
            if self.finetuning_preparator:
                try:
                    ft_recommendations = self.finetuning_preparator.get_dataset_recommendations()
                    stats['finetuning_recommendations'] = ft_recommendations
                except Exception as e:
                    stats['finetuning_error'] = str(e)
            
            # Estatísticas de uso de treinamento
            if self.log_training_usage:
                stats['training_usage_error'] = 'Training logger não disponível'
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def search_training_content(self, query: str, limit: int = 10) -> Dict:
        """
        Busca conteúdo nos dados de treinamento
        """
        try:
            if not self.advanced_rag:
                return {'error': 'Sistema RAG avançado não disponível'}
            
            results = self.advanced_rag.search_training_content(query, limit)
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'total_found': len(results)
            }
            
        except Exception as e:
            logger.error(f"Erro na busca de conteúdo: {e}")
            return {'error': str(e)}
    
    def create_finetuning_dataset(self, dataset_type: str = 'hybrid', 
                                 format_type: str = 'openai_chat',
                                 max_samples: int = 1000) -> Dict:
        """
        Cria dataset para fine-tuning
        
        Args:
            dataset_type: Tipo do dataset ('conversations', 'training_data', 'hybrid')
            format_type: Formato ('openai_chat', 'jsonl', 'csv')
            max_samples: Número máximo de amostras
        """
        try:
            if not self.finetuning_preparator:
                return {'error': 'Preparador de fine-tuning não disponível'}
            
            print(f"FINETUNING_DATASET: Criando dataset {dataset_type} formato {format_type}")
            
            if dataset_type == 'conversations':
                result = self.finetuning_preparator.create_conversation_dataset(
                    format_type=format_type,
                    max_samples=max_samples
                )
            elif dataset_type == 'training_data':
                result = self.finetuning_preparator.create_training_data_dataset(
                    format_type=format_type,
                    max_samples=max_samples
                )
            elif dataset_type == 'hybrid':
                result = self.finetuning_preparator.create_hybrid_dataset(
                    total_samples=max_samples,
                    format_type=format_type
                )
            else:
                return {'error': f'Tipo de dataset não suportado: {dataset_type}'}
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na criação do dataset: {e}")
            return {'error': str(e)}
    
    def save_finetuning_dataset(self, dataset_result: Dict, file_path: str = None) -> Dict:
        """
        Salva dataset de fine-tuning em arquivo
        """
        try:
            if not self.finetuning_preparator:
                return {'error': 'Preparador de fine-tuning não disponível'}
            
            return self.finetuning_preparator.save_dataset_to_file(dataset_result, file_path)
            
        except Exception as e:
            logger.error(f"Erro ao salvar dataset: {e}")
            return {'error': str(e)}
    
    def get_advanced_context(self, user_message: str, risk_level: str = 'low',
                           context_type: str = 'all') -> Dict:
        """
        Obtém contexto avançado usando RAG
        """
        try:
            if not self.advanced_rag:
                return {'error': 'Sistema RAG avançado não disponível'}
            
            return self.advanced_rag.get_enhanced_context(
                user_message, risk_level, context_type
            )
            
        except Exception as e:
            logger.error(f"Erro no contexto avançado: {e}")
            return {'error': str(e)}
    
    def analyze_prompt_context(self, user_message: str, risk_level: str = 'low',
                             user_context: Optional[Dict] = None) -> Dict:
        """
        Analisa contexto para prompt engineering
        """
        try:
            if not self.prompt_manager:
                return {'error': 'Sistema de prompt engineering não disponível'}
            
            # PromptContext, RiskLevel já importados no topo
            
            # Criar contexto
            prompt_context = PromptContext(
                user_message=user_message,
                risk_level=RiskLevel(risk_level),
                user_name=user_context.get('name') if user_context else None
            )
            
            # Validar contexto
            is_valid, errors = self.prompt_manager.validate_prompt_context(prompt_context)
            
            # Construir prompt de exemplo
            prompt_data = self.prompt_manager.build_contextual_prompt(
                prompt_context, provider='openai'
            )
            
            return {
                'success': True,
                'context_valid': is_valid,
                'validation_errors': errors,
                'prompt_preview': {
                    'system_message': prompt_data['messages'][0]['content'][:500] + '...',
                    'user_message': prompt_data['messages'][-1]['content'],
                    'total_messages': len(prompt_data['messages']),
                    'max_tokens': prompt_data['max_tokens'],
                    'temperature': prompt_data['temperature']
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na análise do prompt: {e}")
            return {'error': str(e)}
    
    def get_system_capabilities(self) -> Dict:
        """
        Retorna capacidades completas do sistema
        """
        return {
            'core_features': {
                'sentiment_analysis': True,
                'risk_assessment': True,
                'response_generation': True,
                'diary_analysis': True
            },
            'advanced_features': {
                'advanced_rag': bool(self.advanced_rag),
                'consolidated_prompt_engineering': bool(self.prompt_manager),
                'finetuning_preparation': bool(self.finetuning_preparator),
                'training_usage_logging': self.log_training_usage
            },
            'supported_formats': {
                'finetuning': ['openai_chat', 'openai_completion', 'jsonl', 'csv'],
                'rag_context': ['training_data', 'conversações', 'hybrid']
            },
            'models': self.get_model_info(),
            'version': '3.0 - Integrated Advanced System'
        }
    
    def get_training_usage_report(self) -> Dict:
        """
        Retorna relatório detalhado do uso de dados de treinamento
        """
        return {'error': 'Training logger não está disponível'}
    
    def clear_training_cache(self) -> Dict:
        """
        Limpa o cache de dados de treinamento
        """
        return {'error': 'Training logger não está disponível'}


# === FUNÇÕES DE CONVENIÊNCIA ===

def create_ai_service(app=None) -> AIService:
    """Cria instância configurada do AIService"""
    return AIService(app)

# Alias para compatibilidade
EmotionalSupportAgent = AIService

