"""
Serviço de treinamento e embeddings para melhorar as respostas da IA
"""

import numpy as np
from typing import List, Dict, Tuple
import openai
from sqlalchemy import text
from app import db
from app.models import ChatMessage, DiaryEntry
import logging

logger = logging.getLogger(__name__)


class AITrainingService:
    """Serviço para treinamento contínuo da IA usando embeddings"""
    
    def __init__(self):
        self.openai_client = openai
        self.embedding_model = "text-embedding-ada-002"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return None
    
    def store_conversation_embedding(self, message_id: int = None, 
                                   diary_id: int = None, text: str = None,
                                   risk_level: str = None, sentiment_score: float = None):
        """Armazena embedding de conversa no banco"""
        if not text:
            return False
            
        embedding = self.generate_embedding(text)
        if not embedding:
            return False
        
        try:
            # Converter embedding para formato PostgreSQL
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            query = text("""
                INSERT INTO conversation_embeddings 
                (chat_message_id, diary_entry_id, embedding, risk_level, sentiment_score)
                VALUES (:message_id, :diary_id, :embedding::vector, :risk_level, :sentiment_score)
            """)
            
            db.session.execute(query, {
                'message_id': message_id,
                'diary_id': diary_id,
                'embedding': embedding_str,
                'risk_level': risk_level,
                'sentiment_score': sentiment_score
            })
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar embedding: {e}")
            db.session.rollback()
            return False
    
    def find_similar_conversations(self, text: str, limit: int = 5) -> List[Dict]:
        """Encontra conversas similares usando busca vetorial"""
        embedding = self.generate_embedding(text)
        if not embedding:
            return []
        
        try:
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            
            query = text("""
                SELECT 
                    ce.id,
                    ce.chat_message_id,
                    ce.diary_entry_id,
                    ce.risk_level,
                    ce.sentiment_score,
                    cm.content as message_content,
                    de.content as diary_content,
                    (ce.embedding <=> :embedding::vector) as similarity_distance
                FROM conversation_embeddings ce
                LEFT JOIN chat_messages cm ON ce.chat_message_id = cm.id
                LEFT JOIN diary_entries de ON ce.diary_entry_id = de.id
                ORDER BY ce.embedding <=> :embedding::vector
                LIMIT :limit
            """)
            
            result = db.session.execute(query, {
                'embedding': embedding_str,
                'limit': limit
            })
            
            return [dict(row._mapping) for row in result]
            
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {e}")
            return []
    
    def get_contextual_response_suggestions(self, user_message: str, 
                                          risk_level: str) -> List[str]:
        """Gera sugestões de resposta baseadas em conversas similares"""
        similar_convs = self.find_similar_conversations(user_message)
        
        suggestions = []
        for conv in similar_convs:
            # Buscar resposta da IA para essa conversa similar
            if conv['chat_message_id']:
                # Buscar próxima mensagem da IA na mesma sessão
                next_ai_msg = ChatMessage.query.filter(
                    ChatMessage.session_id == ChatMessage.query.get(
                        conv['chat_message_id']
                    ).session_id,
                    ChatMessage.id > conv['chat_message_id'],
                    ChatMessage.message_type == 'AI'
                ).first()
                
                if next_ai_msg and len(suggestions) < 3:
                    suggestions.append(next_ai_msg.content)
        
        return suggestions
    
    def train_from_successful_conversations(self):
        """Treina usando conversas bem avaliadas"""
        # Buscar conversas com boa avaliação (4-5 estrelas)
        successful_sessions = db.session.execute(text("""
            SELECT cs.id, cs.user_rating
            FROM chat_sessions cs
            WHERE cs.user_rating >= 4
            AND cs.ended_at IS NOT NULL
        """)).fetchall()
        
        processed = 0
        for session in successful_sessions:
            # Processar mensagens dessa sessão
            messages = ChatMessage.query.filter_by(
                session_id=session.id
            ).order_by(ChatMessage.created_at).all()
            
            for msg in messages:
                if msg.message_type == 'USER':
                    # Armazenar embedding da mensagem do usuário
                    self.store_conversation_embedding(
                        message_id=msg.id,
                        text=msg.content,
                        risk_level=msg.risk_indicators,
                        sentiment_score=msg.sentiment_score
                    )
                    processed += 1
        
        logger.info(f"Processadas {processed} mensagens para treinamento")
        return processed
    
    def analyze_conversation_patterns(self) -> Dict:
        """Analisa padrões nas conversas para insights"""
        try:
            # Análise de eficácia por nível de risco
            risk_analysis = db.session.execute(text("""
                SELECT 
                    ce.risk_level,
                    COUNT(*) as total_conversations,
                    AVG(cs.user_rating) as avg_rating,
                    AVG(cs.duration_minutes) as avg_duration
                FROM conversation_embeddings ce
                JOIN chat_messages cm ON ce.chat_message_id = cm.id
                JOIN chat_sessions cs ON cm.session_id = cs.id
                WHERE cs.user_rating IS NOT NULL
                GROUP BY ce.risk_level
            """)).fetchall()
            
            # Análise de sentimentos
            sentiment_analysis = db.session.execute(text("""
                SELECT 
                    CASE 
                        WHEN ce.sentiment_score >= 0.3 THEN 'positive'
                        WHEN ce.sentiment_score <= -0.3 THEN 'negative'
                        ELSE 'neutral'
                    END as sentiment_category,
                    COUNT(*) as count,
                    AVG(cs.user_rating) as avg_rating
                FROM conversation_embeddings ce
                JOIN chat_messages cm ON ce.chat_message_id = cm.id
                JOIN chat_sessions cs ON cm.session_id = cs.id
                WHERE cs.user_rating IS NOT NULL
                GROUP BY sentiment_category
            """)).fetchall()
            
            return {
                'risk_patterns': [dict(row._mapping) for row in risk_analysis],
                'sentiment_patterns': [dict(row._mapping) for row in sentiment_analysis],
                'total_embeddings': self.get_embedding_count()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de padrões: {e}")
            return {}
    
    def get_embedding_count(self) -> int:
        """Retorna número total de embeddings armazenados"""
        try:
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM conversation_embeddings"
            )).scalar()
            return result or 0
        except:
            return 0


# Função para migração/setup inicial
def setup_embeddings_table():
    """Cria tabela de embeddings se não existir"""
    try:
        db.session.execute(text("""
            CREATE EXTENSION IF NOT EXISTS vector;
            
            CREATE TABLE IF NOT EXISTS conversation_embeddings (
                id SERIAL PRIMARY KEY,
                chat_message_id INTEGER REFERENCES chat_messages(id),
                diary_entry_id INTEGER REFERENCES diary_entries(id),
                embedding vector(1536),
                risk_level VARCHAR(20),
                sentiment_score FLOAT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_conversation_embeddings_vector 
            ON conversation_embeddings USING ivfflat (embedding vector_cosine_ops);
        """))
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabela de embeddings: {e}")
        db.session.rollback()
        return False
