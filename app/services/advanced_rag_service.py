"""
Sistema RAG Avançado com Integração de Dados de Treinamento
Combina Retrieval-Augmented Generation com dados específicos do domínio
"""

import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import text, desc
from app import db
from app.models.training import TrainingData
import openai
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class AdvancedRAGService:
    """
    Sistema RAG Profissional para Suporte Emocional
    
    Funcionalidades:
    - Busca em dados de treinamento aprovados
    - Busca em conversas bem-sucedidas
    - Embeddings semânticos quando disponível
    - Ranqueamento por relevância e qualidade
    - Cache inteligente
    - Prompt engineering avançado
    """
    
    def __init__(self):
        self.openai_client = openai
        self.embedding_model = "text-embedding-3-small"  # Modelo mais barato
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        self.max_context_length = 4000  # Tokens
        
        logger.info("AdvancedRAGService inicializado")
    
    def get_enhanced_context(self, user_message: str, risk_level: str = 'low', 
                           context_type: str = 'all', limit: int = 3) -> Dict:
        """
        Busca contexto avançado combinando múltiplas fontes
        
        Args:
            user_message: Mensagem do usuário
            risk_level: Nível de risco (low, moderate, high, critical)
            context_type: Tipo de contexto ('training', 'conversations', 'all')
            limit: Número máximo de resultados por fonte
            
        Returns:
            Dict com contexto estruturado e metadados
        """
        try:
            # Verificar cache
            cache_key = f"enhanced_{hash(user_message)}_{risk_level}_{context_type}_{limit}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
            
            result = {
                'training_data': [],
                'conversation_examples': [],
                'context_prompt': '',
                'metadata': {
                    'sources_used': [],
                    'relevance_scores': [],
                    'timestamp': datetime.utcnow().isoformat(),
                    'risk_level': risk_level
                }
            }
            
            # 1. Buscar dados de treinamento relevantes
            if context_type in ['training', 'all']:
                training_context = self._search_training_data(user_message, risk_level, limit)
                result['training_data'] = training_context
                if training_context:
                    result['metadata']['sources_used'].append('training_data')
            
            # 2. Buscar conversas bem-sucedidas
            if context_type in ['conversations', 'all']:
                conversation_context = self._search_successful_conversations(user_message, risk_level, limit)
                result['conversation_examples'] = conversation_context
                if conversation_context:
                    result['metadata']['sources_used'].append('conversations')
            
            # 3. Construir prompt contextualizado
            result['context_prompt'] = self._build_enhanced_prompt(
                user_message, risk_level, result['training_data'], result['conversation_examples']
            )
            
            # 4. Calcular scores de relevância
            result['metadata']['relevance_scores'] = self._calculate_relevance_scores(result)
            
            # Cache do resultado
            self._cache_result(cache_key, result)
            
            print(f"RAG_CONTEXT_FOUND: {len(result['training_data'])} dados de treinamento, {len(result['conversation_examples'])} conversas")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no contexto avançado: {e}")
            return self._get_fallback_context(user_message, risk_level)
    
    def _search_training_data(self, user_message: str, risk_level: str, limit: int) -> List[Dict]:
        """Busca dados de treinamento relevantes"""
        try:
            # Extrair palavras-chave
            keywords = self._extract_mental_health_keywords(user_message)
            
            # Query para buscar dados de treinamento aprovados
            training_data = []
            
            # Busca por similaridade de texto
            query = text("""
                SELECT 
                    id, title, content, file_path, score, created_at,
                    CASE 
                        WHEN title IS NOT NULL THEN title
                        WHEN file_path IS NOT NULL THEN 
                            SUBSTRING(file_path FROM '[^/]*$')
                        ELSE 'Dados de Treinamento'
                    END as display_title
                FROM training_data 
                WHERE status = 'APPROVED'
                AND (
                    LOWER(content) SIMILAR TO :keyword_pattern
                    OR LOWER(title) SIMILAR TO :keyword_pattern
                )
                ORDER BY 
                    score DESC,
                    LENGTH(content) DESC,
                    created_at DESC
                LIMIT :limit
            """)
            
            # Criar padrão de busca
            if keywords:
                keyword_pattern = f"%({'|'.join([k for k in keywords if len(k) > 3])})%"
            else:
                keyword_pattern = f"%{user_message.lower()[:50]}%"
            
            result = db.session.execute(query, {
                'keyword_pattern': keyword_pattern,
                'limit': limit * 2  # Buscar mais para filtrar
            })
            
            for row in result:
                # Calcular relevância
                relevance = self._calculate_text_relevance(user_message, row.content)
                
                if relevance > 0.1:  # Threshold mínimo
                    training_data.append({
                        'id': row.id,
                        'title': row.display_title,
                        'content': self._truncate_content(row.content, 800),
                        'relevance_score': relevance,
                        'source': 'training_data',
                        'file_path': row.file_path,
                        'created_at': row.created_at.isoformat() if row.created_at else None
                    })
            
            # Ordenar por relevância e retornar os melhores
            training_data.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            print(f"TRAINING_DATA_SEARCH: Encontrados {len(training_data)} dados relevantes")
            
            return training_data[:limit]
            
        except Exception as e:
            logger.error(f"Erro na busca de dados de treinamento: {e}")
            return []
    
    def _search_successful_conversations(self, user_message: str, risk_level: str, limit: int) -> List[Dict]:
        """Busca conversas bem-sucedidas similares"""
        try:
            keywords = self._extract_mental_health_keywords(user_message)
            keyword_pattern = '|'.join([k for k in keywords if len(k) > 3]) if keywords else ''
            
            query = text("""
                SELECT DISTINCT
                    cm_user.content as user_message,
                    cm_ai.content as ai_response,
                    cs.user_rating,
                    cs.initial_risk_level,
                    cm_ai.created_at,
                    cs.resolution_type
                FROM chat_sessions cs
                JOIN chat_messages cm_user ON cs.id = cm_user.session_id 
                    AND cm_user.message_type = 'USER'
                JOIN chat_messages cm_ai ON cs.id = cm_ai.session_id 
                    AND cm_ai.message_type = 'AI'
                    AND cm_ai.id > cm_user.id
                    AND cm_ai.id = (
                        SELECT MIN(cm2.id) 
                        FROM chat_messages cm2 
                        WHERE cm2.session_id = cs.id 
                        AND cm2.message_type = 'AI' 
                        AND cm2.id > cm_user.id
                    )
                WHERE 
                    cs.user_rating >= 4
                    AND (cs.initial_risk_level = :risk_level OR :risk_level = 'any')
                    AND (:keyword_pattern = '' OR cm_user.content ~* :keyword_pattern)
                    AND cm_user.created_at >= NOW() - INTERVAL '12 months'
                    AND LENGTH(cm_user.content) > 15
                    AND LENGTH(cm_ai.content) > 30
                    AND cs.resolution_type != 'abandoned'
                ORDER BY 
                    cs.user_rating DESC,
                    cm_ai.created_at DESC
                LIMIT :limit
            """)
            
            result = db.session.execute(query, {
                'risk_level': risk_level,
                'keyword_pattern': keyword_pattern,
                'limit': limit * 2
            })
            
            conversations = []
            for row in result:
                # Calcular relevância
                relevance = self._calculate_text_relevance(user_message, row.user_message)
                
                if relevance > 0.15:  # Threshold um pouco maior para conversas
                    conversations.append({
                        'user_message': self._truncate_content(row.user_message, 300),
                        'ai_response': self._truncate_content(row.ai_response, 400),
                        'rating': row.user_rating,
                        'risk_level': row.initial_risk_level,
                        'relevance_score': relevance,
                        'source': 'conversation',
                        'resolution_type': row.resolution_type,
                        'created_at': row.created_at.isoformat() if row.created_at else None
                    })
            
            # Ordenar por relevância
            conversations.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            print(f"CONVERSATION_SEARCH: Encontradas {len(conversations)} conversas relevantes")
            
            return conversations[:limit]
            
        except Exception as e:
            logger.error(f"Erro na busca de conversas: {e}")
            return []
    
    def _extract_mental_health_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave específicas de saúde mental"""
        mental_health_terms = {
            # Emoções e sentimentos
            'emoções': ['ansiedade', 'depressão', 'tristeza', 'medo', 'raiva', 'solidão', 'vazio', 'culpa', 'vergonha', 'desesperança'],
            
            # Sintomas e manifestações
            'sintomas': ['pânico', 'insônia', 'pesadelos', 'irritabilidade', 'cansaço', 'falta de energia', 'concentração', 'memória'],
            
            # Contextos de vida
            'contextos': ['trabalho', 'família', 'relacionamento', 'escola', 'faculdade', 'amigos', 'dinheiro', 'saúde', 'futuro'],
            
            # Comportamentos
            'comportamentos': ['isolamento', 'evitação', 'procrastinação', 'compulsão', 'vício', 'autolesão'],
            
            # Pensamentos
            'pensamentos': ['negativo', 'catastrófico', 'ruminação', 'obsessivo', 'suicida', 'morte', 'fracasso'],
            
            # Coping e recursos
            'recursos': ['terapia', 'medicação', 'apoio', 'estratégia', 'técnica', 'respiração', 'meditação', 'exercício']
        }
        
        text_lower = text.lower()
        found_keywords = []
        
        # Buscar termos específicos
        for category, terms in mental_health_terms.items():
            for term in terms:
                if term in text_lower:
                    found_keywords.append(term)
        
        # Adicionar palavras importantes (não muito comuns)
        words = re.findall(r'\b[a-záêç]+\b', text_lower)
        important_words = [w for w in words if len(w) > 4 and w not in ['sobre', 'muito', 'sempre', 'quando', 'porque', 'depois']]
        found_keywords.extend(important_words[:10])
        
        return list(set(found_keywords))[:15]
    
    def _calculate_text_relevance(self, query: str, text: str) -> float:
        """Calcula relevância entre dois textos"""
        try:
            query_words = set(re.findall(r'\b[a-záêç]+\b', query.lower()))
            text_words = set(re.findall(r'\b[a-záêç]+\b', text.lower()))
            
            if not query_words:
                return 0.0
            
            # Interseção de palavras
            common_words = query_words.intersection(text_words)
            word_overlap = len(common_words) / len(query_words)
            
            # Bonus para palavras importantes de saúde mental
            mental_health_bonus = 0
            mental_health_keywords = [
                'ansiedade', 'depressão', 'tristeza', 'medo', 'estresse', 'pânico',
                'família', 'trabalho', 'relacionamento', 'futuro', 'ajuda', 'apoio'
            ]
            
            for keyword in mental_health_keywords:
                if keyword in text.lower() and keyword in query.lower():
                    mental_health_bonus += 0.1
            
            # Score final
            relevance = min(1.0, word_overlap + mental_health_bonus)
            
            return relevance
            
        except Exception:
            return 0.0
    
    def _build_enhanced_prompt(self, user_message: str, risk_level: str, 
                             training_data: List[Dict], conversations: List[Dict]) -> str:
        """Constrói prompt avançado com contexto"""
        prompt_parts = []
        
        # Seção de dados de treinamento
        if training_data:
            prompt_parts.append("=== CONHECIMENTO ESPECIALIZADO ===")
            for i, data in enumerate(training_data[:2], 1):  # Máximo 2 para não sobrecarregar
                title = data.get('title', 'Documento')
                content = data['content']
                prompt_parts.append(f"📚 Fonte {i}: {title}")
                prompt_parts.append(f"Conteúdo: {content}")
                prompt_parts.append("")
        
        # Seção de exemplos de conversas
        if conversations:
            prompt_parts.append("=== EXEMPLOS DE RESPOSTAS EFICAZES ===")
            for i, conv in enumerate(conversations[:2], 1):  # Máximo 2
                rating = "⭐" * int(conv['rating'])
                prompt_parts.append(f"💬 Exemplo {i} ({rating}):")
                prompt_parts.append(f"Situação similar: {conv['user_message']}")
                prompt_parts.append(f"Resposta que funcionou: {conv['ai_response']}")
                prompt_parts.append("")
        
        # Instruções contextualizadas
        if training_data or conversations:
            prompt_parts.append("=== INSTRUÇÕES ESPECÍFICAS ===")
            
            if risk_level in ['high', 'critical']:
                prompt_parts.append("⚠️ SITUAÇÃO DE ALTO RISCO - Priorizar segurança e encaminhamento profissional")
            
            if training_data:
                prompt_parts.append("📖 Use o conhecimento especializado acima para fundamentar sua resposta")
            
            if conversations:
                prompt_parts.append("💡 Inspire-se nos exemplos eficazes, mas adapte para o contexto atual")
            
            prompt_parts.append("🎯 Seja empático, prático e ofereça suporte concreto")
            prompt_parts.append("")
        
        return "\n".join(prompt_parts) if prompt_parts else ""
    
    def _truncate_content(self, content: str, max_length: int) -> str:
        """Trunca conteúdo mantendo contexto"""
        if len(content) <= max_length:
            return content
        
        # Tentar cortar em uma frase completa
        sentences = content.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + ".") <= max_length - 3:
                truncated += sentence + "."
            else:
                break
        
        if not truncated:  # Se nenhuma frase coube, cortar no meio
            truncated = content[:max_length-3]
        
        return truncated + "..."
    
    def _calculate_relevance_scores(self, result: Dict) -> Dict:
        """Calcula scores de relevância agregados"""
        scores = {
            'training_data_avg': 0.0,
            'conversations_avg': 0.0,
            'overall_quality': 0.0
        }
        
        # Score médio dos dados de treinamento
        if result['training_data']:
            scores['training_data_avg'] = sum(
                item['relevance_score'] for item in result['training_data']
            ) / len(result['training_data'])
        
        # Score médio das conversas
        if result['conversation_examples']:
            scores['conversations_avg'] = sum(
                item['relevance_score'] for item in result['conversation_examples']
            ) / len(result['conversation_examples'])
        
        # Qualidade geral (combina ambos)
        total_sources = len(result['training_data']) + len(result['conversation_examples'])
        if total_sources > 0:
            weighted_score = (
                scores['training_data_avg'] * len(result['training_data']) * 1.2 +  # Bonus para dados de treinamento
                scores['conversations_avg'] * len(result['conversation_examples'])
            ) / (len(result['training_data']) * 1.2 + len(result['conversation_examples']))
            
            scores['overall_quality'] = weighted_score
        
        return scores
    
    def _get_fallback_context(self, user_message: str, risk_level: str) -> Dict:
        """Contexto de fallback quando a busca falha"""
        return {
            'training_data': [],
            'conversation_examples': [],
            'context_prompt': f"Responda com empatia para uma situação de nível de risco {risk_level}.",
            'metadata': {
                'sources_used': ['fallback'],
                'relevance_scores': {'overall_quality': 0.1},
                'timestamp': datetime.utcnow().isoformat(),
                'risk_level': risk_level
            }
        }
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Recupera item do cache se válido"""
        try:
            if key in self.cache:
                item = self.cache[key]
                if datetime.utcnow().timestamp() - item['timestamp'] < self.cache_ttl:
                    return item['data']
                else:
                    del self.cache[key]
            return None
        except Exception:
            return None
    
    def _cache_result(self, key: str, result: Dict) -> None:
        """Armazena resultado no cache"""
        try:
            # Limpar cache se estiver muito grande
            if len(self.cache) > 100:
                # Remove 20% dos itens mais antigos
                sorted_items = sorted(
                    self.cache.items(), 
                    key=lambda x: x[1]['timestamp']
                )
                for old_key, _ in sorted_items[:20]:
                    del self.cache[old_key]
            
            self.cache[key] = {
                'data': result,
                'timestamp': datetime.utcnow().timestamp()
            }
        except Exception as e:
            logger.warning(f"Erro no cache: {e}")
    
    def get_training_data_statistics(self) -> Dict:
        """Retorna estatísticas dos dados de treinamento"""
        try:
            stats = {}
            
            # Contagem geral
            general_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'APPROVED' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                    COUNT(CASE WHEN file_path IS NOT NULL THEN 1 END) as file_uploads,
                    COUNT(CASE WHEN title IS NOT NULL THEN 1 END) as text_entries,
                    AVG(score) as avg_score
                FROM training_data
            """)).fetchone()
            
            if general_stats:
                stats['general'] = dict(general_stats._mapping)
            
            # Distribuição por tamanho de conteúdo
            size_stats = db.session.execute(text("""
                SELECT 
                    CASE 
                        WHEN LENGTH(content) < 1000 THEN 'small'
                        WHEN LENGTH(content) < 5000 THEN 'medium'
                        WHEN LENGTH(content) < 20000 THEN 'large'
                        ELSE 'very_large'
                    END as size_category,
                    COUNT(*) as count,
                    AVG(score) as avg_score
                FROM training_data
                WHERE status = 'APPROVED'
                GROUP BY size_category
            """)).fetchall()
            
            stats['size_distribution'] = [dict(row._mapping) for row in size_stats]
            
            # Dados recentes
            recent_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as recent_count,
                    AVG(score) as recent_avg_score
                FROM training_data
                WHERE status = 'APPROVED'
                AND created_at >= NOW() - INTERVAL '30 days'
            """)).fetchone()
            
            if recent_stats:
                stats['recent'] = dict(recent_stats._mapping)
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro nas estatísticas: {e}")
            return {'error': str(e)}
    
    def search_training_content(self, query: str, limit: int = 10) -> List[Dict]:
        """Busca específica em conteúdo de treinamento"""
        try:
            # Busca textual
            result = db.session.execute(text("""
                SELECT 
                    id, title, content, file_path, score, created_at,
                    ts_rank(to_tsvector('portuguese', content), plainto_tsquery('portuguese', :query)) as rank
                FROM training_data
                WHERE status = 'APPROVED'
                AND (
                    to_tsvector('portuguese', content) @@ plainto_tsquery('portuguese', :query)
                    OR LOWER(content) LIKE LOWER(:like_query)
                    OR LOWER(title) LIKE LOWER(:like_query)
                )
                ORDER BY rank DESC, score DESC, created_at DESC
                LIMIT :limit
            """), {
                'query': query,
                'like_query': f'%{query}%',
                'limit': limit
            })
            
            results = []
            for row in result:
                content_preview = self._truncate_content(row.content, 200)
                results.append({
                    'id': row.id,
                    'title': row.title or 'Documento de Treinamento',
                    'content_preview': content_preview,
                    'file_path': row.file_path,
                    'score': row.score,
                    'relevance_rank': float(row.rank) if row.rank else 0.0,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro na busca de conteúdo: {e}")
            return []


# Instância global para uso fácil
advanced_rag_service = AdvancedRAGService()