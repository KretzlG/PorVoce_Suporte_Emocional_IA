"""
Módulo de Preparação para Fine-tuning de Modelos de IA
Prepara datasets de conversas e dados de treinamento para fine-tuning
"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from pathlib import Path
import hashlib
import openai

# Pandas é opcional - usado apenas para análise avançada
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from app import db
from app.models.training import TrainingData
from app.models.chat import ChatSession, ChatMessage

logger = logging.getLogger(__name__)


class FinetuningDatasetPreparator:
    """
    Preparador de Datasets para Fine-tuning
    
    Funcionalidades:
    - Extração de conversas bem-sucedidas
    - Formatação para diferentes provedores (OpenAI, Gemini, etc.)
    - Validação e limpeza de dados
    - Geração de datasets balanceados
    - Análise de qualidade dos dados
    """
    
    def __init__(self):
        self.openai_client = openai
        self.supported_formats = ['openai_chat', 'openai_completion', 'jsonl', 'csv']
        self.quality_thresholds = {
            'min_rating': 4,
            'min_message_length': 20,
            'max_message_length': 2000,
            'min_response_length': 30,
            'max_response_length': 1000
        }
        logger.info("FinetuningDatasetPreparator inicializado")
    
    def create_conversation_dataset(self, 
                                  format_type: str = 'openai_chat',
                                  min_rating: int = 4,
                                  months_back: int = 12,
                                  max_samples: int = 1000,
                                  balance_risk_levels: bool = True) -> Dict:
        """
        Cria dataset de conversas para fine-tuning
        
        Args:
            format_type: Formato do dataset ('openai_chat', 'openai_completion', 'jsonl', 'csv')
            min_rating: Rating mínimo das conversas (1-5)
            months_back: Meses para trás para buscar conversas
            max_samples: Número máximo de amostras
            balance_risk_levels: Se deve balancear por níveis de risco
            
        Returns:
            Dict com dataset e metadados
        """
        try:
            print(f"DATASET_CREATION: Iniciando criação de dataset formato {format_type}")
            
            # 1. Extrair conversas de qualidade
            conversations = self._extract_quality_conversations(
                min_rating, months_back, max_samples * 2  # Buscar mais para filtrar
            )
            
            print(f"CONVERSATIONS_EXTRACTED: {len(conversations)} conversas encontradas")
            
            if not conversations:
                return {
                    'success': False,
                    'error': 'Nenhuma conversa de qualidade encontrada',
                    'data': []
                }
            
            # 2. Filtrar e limpar dados
            cleaned_conversations = self._clean_and_filter_conversations(conversations)
            print(f"CONVERSATIONS_CLEANED: {len(cleaned_conversations)} após limpeza")
            
            # 3. Balancear por níveis de risco se solicitado
            if balance_risk_levels:
                balanced_conversations = self._balance_by_risk_levels(cleaned_conversations, max_samples)
            else:
                balanced_conversations = cleaned_conversations[:max_samples]
            
            print(f"CONVERSATIONS_BALANCED: {len(balanced_conversations)} após balanceamento")
            
            # 4. Formatar para o tipo solicitado
            formatted_data = self._format_dataset(balanced_conversations, format_type)
            
            # 5. Validar dataset
            validation_result = self._validate_dataset(formatted_data, format_type)
            
            # 6. Gerar metadados
            metadata = self._generate_dataset_metadata(
                balanced_conversations, format_type, validation_result
            )
            
            result = {
                'success': True,
                'format': format_type,
                'data': formatted_data,
                'metadata': metadata,
                'validation': validation_result,
                'file_ready': True
            }
            
            print(f"DATASET_READY: {len(formatted_data)} amostras formatadas")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na criação do dataset: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def create_training_data_dataset(self,
                                   format_type: str = 'openai_chat',
                                   include_approved_only: bool = True,
                                   max_samples: int = 500) -> Dict:
        """
        Cria dataset baseado nos dados de treinamento aprovados
        
        Args:
            format_type: Formato do dataset
            include_approved_only: Se deve incluir apenas dados aprovados
            max_samples: Número máximo de amostras
            
        Returns:
            Dict com dataset e metadados
        """
        try:
            print(f"TRAINING_DATASET: Criando dataset de dados de treinamento")
            
            # Buscar dados de treinamento
            query_conditions = ["status = 'APPROVED'"] if include_approved_only else []
            
            query = text(f"""
                SELECT id, title, content, file_path, score, created_at
                FROM training_data
                {('WHERE ' + ' AND '.join(query_conditions)) if query_conditions else ''}
                ORDER BY score DESC, created_at DESC
                LIMIT :max_samples
            """)
            
            result = db.session.execute(query, {'max_samples': max_samples})
            training_data = [dict(row._mapping) for row in result]
            
            if not training_data:
                return {
                    'success': False,
                    'error': 'Nenhum dado de treinamento encontrado',
                    'data': []
                }
            
            # Converter para formato de conversas simuladas
            simulated_conversations = []
            
            for data in training_data:
                # Criar conversas simuladas baseadas no conteúdo
                questions = self._generate_questions_from_content(data['content'])
                
                for question in questions:
                    simulated_conversations.append({
                        'user_message': question,
                        'ai_response': self._extract_relevant_answer(question, data['content']),
                        'user_rating': 5,  # Dados de treinamento têm alta qualidade
                        'risk_level': 'low',  # Assumir baixo risco para dados educacionais
                        'source': 'training_data',
                        'training_data_id': data['id']
                    })
            
            print(f"TRAINING_CONVERSATIONS: {len(simulated_conversations)} conversas simuladas")
            
            # Formatar dataset
            formatted_data = self._format_dataset(simulated_conversations, format_type)
            
            # Validar
            validation_result = self._validate_dataset(formatted_data, format_type)
            
            # Metadados
            metadata = self._generate_dataset_metadata(
                simulated_conversations, format_type, validation_result, source='training_data'
            )
            
            return {
                'success': True,
                'format': format_type,
                'data': formatted_data,
                'metadata': metadata,
                'validation': validation_result,
                'source': 'training_data',
                'file_ready': True
            }
            
        except Exception as e:
            logger.error(f"Erro no dataset de treinamento: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def create_hybrid_dataset(self,
                            conversation_weight: float = 0.7,
                            training_weight: float = 0.3,
                            total_samples: int = 1000,
                            format_type: str = 'openai_chat') -> Dict:
        """
        Cria dataset híbrido combinando conversas reais e dados de treinamento
        
        Args:
            conversation_weight: Peso das conversas reais (0-1)
            training_weight: Peso dos dados de treinamento (0-1)
            total_samples: Total de amostras desejadas
            format_type: Formato do dataset
            
        Returns:
            Dict com dataset híbrido
        """
        try:
            print(f"HYBRID_DATASET: Criando dataset híbrido")
            
            # Calcular amostras por fonte
            conversation_samples = int(total_samples * conversation_weight)
            training_samples = int(total_samples * training_weight)
            
            # Criar datasets separados
            conv_dataset = self.create_conversation_dataset(
                format_type=format_type,
                max_samples=conversation_samples
            )
            
            training_dataset = self.create_training_data_dataset(
                format_type=format_type,
                max_samples=training_samples
            )
            
            if not conv_dataset['success'] and not training_dataset['success']:
                return {
                    'success': False,
                    'error': 'Falha em ambas as fontes de dados',
                    'data': []
                }
            
            # Combinar dados
            combined_data = []
            
            if conv_dataset['success']:
                combined_data.extend(conv_dataset['data'])
                print(f"HYBRID_CONVERSATIONS: {len(conv_dataset['data'])} amostras de conversas")
            
            if training_dataset['success']:
                combined_data.extend(training_dataset['data'])
                print(f"HYBRID_TRAINING: {len(training_dataset['data'])} amostras de treinamento")
            
            # Embaralhar dados
            import random
            random.shuffle(combined_data)
            
            # Metadados combinados
            metadata = {
                'total_samples': len(combined_data),
                'conversation_samples': len(conv_dataset['data']) if conv_dataset['success'] else 0,
                'training_samples': len(training_dataset['data']) if training_dataset['success'] else 0,
                'format': format_type,
                'creation_date': datetime.utcnow().isoformat(),
                'weights': {
                    'conversations': conversation_weight,
                    'training_data': training_weight
                }
            }
            
            print(f"HYBRID_COMPLETE: {len(combined_data)} amostras totais")
            
            return {
                'success': True,
                'format': format_type,
                'data': combined_data,
                'metadata': metadata,
                'type': 'hybrid',
                'file_ready': True
            }
            
        except Exception as e:
            logger.error(f"Erro no dataset híbrido: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def _extract_quality_conversations(self, min_rating: int, months_back: int, 
                                     max_samples: int) -> List[Dict]:
        """Extrai conversas de qualidade do banco"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30 * months_back)
            
            query = text("""
                SELECT DISTINCT
                    cm_user.id as user_msg_id,
                    cm_user.content as user_message,
                    cm_ai.content as ai_response,
                    cs.user_rating,
                    cs.initial_risk_level,
                    cs.resolution_type,
                    cm_user.created_at,
                    cm_ai.sentiment_analysis,
                    cm_user.risk_indicators
                FROM chat_sessions cs
                JOIN chat_messages cm_user ON cs.id = cm_user.session_id 
                    AND cm_user.message_type = 'USER'
                JOIN chat_messages cm_ai ON cs.id = cm_ai.session_id 
                    AND cm_ai.message_type = 'AI'
                    AND cm_ai.id = (
                        SELECT MIN(cm2.id) 
                        FROM chat_messages cm2 
                        WHERE cm2.session_id = cs.id 
                        AND cm2.message_type = 'AI' 
                        AND cm2.id > cm_user.id
                    )
                WHERE 
                    cs.user_rating >= :min_rating
                    AND cm_user.created_at >= :cutoff_date
                    AND LENGTH(cm_user.content) >= :min_msg_length
                    AND LENGTH(cm_ai.content) >= :min_response_length
                    AND LENGTH(cm_user.content) <= :max_msg_length
                    AND LENGTH(cm_ai.content) <= :max_response_length
                    AND cs.resolution_type != 'abandoned'
                    AND cm_user.content !~ '^(oi|olá|ok|obrigado|tchau)$'
                ORDER BY 
                    cs.user_rating DESC,
                    cm_user.created_at DESC
                LIMIT :max_samples
            """)
            
            result = db.session.execute(query, {
                'min_rating': min_rating,
                'cutoff_date': cutoff_date,
                'min_msg_length': self.quality_thresholds['min_message_length'],
                'max_msg_length': self.quality_thresholds['max_message_length'],
                'min_response_length': self.quality_thresholds['min_response_length'],
                'max_response_length': self.quality_thresholds['max_response_length'],
                'max_samples': max_samples
            })
            
            return [dict(row._mapping) for row in result]
            
        except Exception as e:
            logger.error(f"Erro na extração de conversas: {e}")
            return []
    
    def _clean_and_filter_conversations(self, conversations: List[Dict]) -> List[Dict]:
        """Limpa e filtra conversas"""
        cleaned = []
        
        for conv in conversations:
            try:
                # Limpar textos
                user_msg = self._clean_text(conv['user_message'])
                ai_response = self._clean_text(conv['ai_response'])
                
                # Validar qualidade
                if (self._is_valid_message(user_msg) and 
                    self._is_valid_response(ai_response) and
                    not self._contains_inappropriate_content(user_msg, ai_response)):
                    
                    cleaned.append({
                        'user_message': user_msg,
                        'ai_response': ai_response,
                        'user_rating': conv['user_rating'],
                        'risk_level': conv['initial_risk_level'] or 'low',
                        'resolution_type': conv['resolution_type'],
                        'created_at': conv['created_at'].isoformat() if conv['created_at'] else None,
                        'quality_score': self._calculate_quality_score(user_msg, ai_response, conv)
                    })
                    
            except Exception as e:
                logger.warning(f"Erro ao limpar conversa: {e}")
                continue
        
        return cleaned
    
    def _balance_by_risk_levels(self, conversations: List[Dict], max_samples: int) -> List[Dict]:
        """Balanceia conversas por níveis de risco"""
        
        # Agrupar por nível de risco
        risk_groups = {
            'low': [],
            'moderate': [],
            'high': [],
            'critical': []
        }
        
        for conv in conversations:
            risk_level = conv.get('risk_level', 'low')
            if risk_level in risk_groups:
                risk_groups[risk_level].append(conv)
        
        # Calcular amostras por grupo (com mínimos)
        min_per_group = max(1, max_samples // 10)  # Pelo menos 10% para cada grupo
        max_per_group = max_samples // 2  # Máximo 50% para um grupo
        
        balanced = []
        remaining_samples = max_samples
        
        # Primeiro, garantir representação mínima
        for risk_level, convs in risk_groups.items():
            if convs and remaining_samples > 0:
                sample_count = min(min_per_group, len(convs), remaining_samples)
                # Pegar as melhores por qualidade
                sorted_convs = sorted(convs, key=lambda x: x.get('quality_score', 0), reverse=True)
                balanced.extend(sorted_convs[:sample_count])
                remaining_samples -= sample_count
        
        # Depois, preencher com as melhores restantes
        if remaining_samples > 0:
            all_remaining = []
            for risk_level, convs in risk_groups.items():
                used_count = len([c for c in balanced if c.get('risk_level') == risk_level])
                remaining_in_group = convs[used_count:]
                all_remaining.extend(remaining_in_group)
            
            # Ordenar por qualidade e pegar as melhores
            all_remaining.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            balanced.extend(all_remaining[:remaining_samples])
        
        return balanced
    
    def _format_dataset(self, conversations: List[Dict], format_type: str) -> List[Dict]:
        """Formata dataset para o tipo especificado"""
        
        if format_type == 'openai_chat':
            return self._format_openai_chat(conversations)
        elif format_type == 'openai_completion':
            return self._format_openai_completion(conversations)
        elif format_type == 'jsonl':
            return self._format_jsonl(conversations)
        elif format_type == 'csv':
            return self._format_csv(conversations)
        else:
            raise ValueError(f"Formato não suportado: {format_type}")
    
    def _format_openai_chat(self, conversations: List[Dict]) -> List[Dict]:
        """Formata para fine-tuning do OpenAI Chat"""
        formatted = []
        
        for conv in conversations:
            # Sistema base para suporte emocional
            system_message = """Você é um assistente especializado em suporte emocional. Seja empático, compreensivo e ofereça orientação prática quando apropriado. Priorize sempre a segurança em situações de risco."""
            
            # Adaptar sistema baseado no risco
            risk_level = conv.get('risk_level', 'low')
            if risk_level in ['high', 'critical']:
                system_message += " Esta é uma situação de alto risco - encoraje busca por ajuda profissional."
            
            formatted.append({
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": conv['user_message']},
                    {"role": "assistant", "content": conv['ai_response']}
                ]
            })
        
        return formatted
    
    def _format_openai_completion(self, conversations: List[Dict]) -> List[Dict]:
        """Formata para fine-tuning do OpenAI Completion (legado)"""
        formatted = []
        
        for conv in conversations:
            formatted.append({
                "prompt": f"Usuário: {conv['user_message']}\\nAssistente:",
                "completion": f" {conv['ai_response']}"
            })
        
        return formatted
    
    def _format_jsonl(self, conversations: List[Dict]) -> List[Dict]:
        """Formata como JSONL genérico"""
        return conversations
    
    def _format_csv(self, conversations: List[Dict]) -> List[Dict]:
        """Formata dados para CSV"""
        formatted = []
        
        for conv in conversations:
            formatted.append({
                'user_message': conv['user_message'],
                'ai_response': conv['ai_response'],
                'rating': conv.get('user_rating', 0),
                'risk_level': conv.get('risk_level', 'low'),
                'quality_score': conv.get('quality_score', 0),
                'created_at': conv.get('created_at', ''),
                'source': conv.get('source', 'conversation')
            })
        
        return formatted
    
    def _generate_questions_from_content(self, content: str) -> List[str]:
        """Gera perguntas baseadas no conteúdo de treinamento"""
        
        # Estratégias para gerar perguntas baseadas no conteúdo
        questions = []
        
        # Padrões simples para começar
        content_lower = content.lower()
        
        # Perguntas sobre sintomas/problemas mencionados
        mental_health_terms = [
            'ansiedade', 'depressão', 'estresse', 'pânico', 'medo',
            'tristeza', 'raiva', 'solidão', 'insônia', 'preocupação'
        ]
        
        for term in mental_health_terms:
            if term in content_lower:
                questions.extend([
                    f"Estou sentindo muita {term}, o que posso fazer?",
                    f"Como lidar com {term}?",
                    f"Tenho {term} constante, isso é normal?"
                ])
        
        # Perguntas sobre contextos mencionados
        contexts = ['trabalho', 'família', 'relacionamento', 'escola', 'futuro']
        
        for context in contexts:
            if context in content_lower:
                questions.extend([
                    f"Estou tendo problemas no {context}",
                    f"Como melhorar minha situação no {context}?",
                    f"Preciso de ajuda com {context}"
                ])
        
        # Limitar e retornar apenas algumas perguntas únicas
        unique_questions = list(set(questions))
        return unique_questions[:3]  # Máximo 3 perguntas por conteúdo
    
    def _extract_relevant_answer(self, question: str, content: str) -> str:
        """Extrai resposta relevante do conteúdo"""
        
        # Simplificado: pega os primeiros parágrafos relevantes
        sentences = content.split('.')
        relevant_sentences = []
        
        question_words = set(question.lower().split())
        
        for sentence in sentences[:10]:  # Primeiras 10 frases
            sentence_words = set(sentence.lower().split())
            common_words = len(question_words.intersection(sentence_words))
            
            if common_words >= 2 and len(sentence.strip()) > 20:
                relevant_sentences.append(sentence.strip())
            
            if len(relevant_sentences) >= 3:  # Máximo 3 frases
                break
        
        if relevant_sentences:
            answer = '. '.join(relevant_sentences) + '.'
            # Limitar tamanho
            if len(answer) > 300:
                answer = answer[:297] + '...'
            return answer
        
        # Fallback: primeira parte do conteúdo
        return content[:200] + '...' if len(content) > 200 else content
    
    def _clean_text(self, text: str) -> str:
        """Limpa texto removendo caracteres desnecessários"""
        if not text:
            return ""
        
        # Remover quebras de linha extras
        text = ' '.join(text.split())
        
        # Remover caracteres de controle
        text = ''.join(char for char in text if ord(char) >= 32)
        
        return text.strip()
    
    def _is_valid_message(self, message: str) -> bool:
        """Valida se uma mensagem é adequada"""
        if not message or len(message) < 10:
            return False
        
        # Verificar se não é apenas saudações
        greetings = ['oi', 'olá', 'ola', 'hey', 'eai', 'e ai']
        if message.lower().strip() in greetings:
            return False
        
        return True
    
    def _is_valid_response(self, response: str) -> bool:
        """Valida se uma resposta é adequada"""
        if not response or len(response) < 20:
            return False
        
        # Verificar se contém conteúdo útil
        if len(response.split()) < 5:
            return False
        
        return True
    
    def _contains_inappropriate_content(self, message: str, response: str) -> bool:
        """Verifica se há conteúdo inapropriado"""
        
        inappropriate_terms = [
            'spam', 'teste', 'test', 'asdfgh', '123456',
            'propaganda', 'venda', 'comprar', 'desconto'
        ]
        
        combined_text = (message + ' ' + response).lower()
        
        return any(term in combined_text for term in inappropriate_terms)
    
    def _calculate_quality_score(self, user_msg: str, ai_response: str, conv: Dict) -> float:
        """Calcula score de qualidade da conversa"""
        
        score = 0.0
        
        # Base: rating do usuário (peso 40%)
        rating = conv.get('user_rating', 3)
        score += (rating / 5.0) * 0.4
        
        # Comprimento adequado (peso 20%)
        msg_len = len(user_msg)
        response_len = len(ai_response)
        
        if 20 <= msg_len <= 200 and 30 <= response_len <= 300:
            score += 0.2
        elif 10 <= msg_len <= 500 and 20 <= response_len <= 500:
            score += 0.1
        
        # Diversidade de palavras (peso 20%)
        msg_words = len(set(user_msg.lower().split()))
        response_words = len(set(ai_response.lower().split()))
        
        if msg_words >= 5 and response_words >= 8:
            score += 0.2
        elif msg_words >= 3 and response_words >= 5:
            score += 0.1
        
        # Tipo de resolução (peso 20%)
        resolution = conv.get('resolution_type', '')
        if resolution == 'positive':
            score += 0.2
        elif resolution == 'neutral':
            score += 0.1
        
        return min(1.0, score)
    
    def _validate_dataset(self, formatted_data: List[Dict], format_type: str) -> Dict:
        """Valida dataset formatado"""
        
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_samples': len(formatted_data),
                'valid_samples': 0,
                'avg_message_length': 0,
                'avg_response_length': 0
            }
        }
        
        try:
            valid_count = 0
            total_msg_len = 0
            total_resp_len = 0
            
            for i, item in enumerate(formatted_data):
                try:
                    if format_type == 'openai_chat':
                        if 'messages' not in item:
                            validation['errors'].append(f"Item {i}: missing 'messages' field")
                            continue
                        
                        messages = item['messages']
                        if len(messages) < 2:
                            validation['errors'].append(f"Item {i}: insufficient messages")
                            continue
                        
                        user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '')
                        ai_msg = next((m['content'] for m in messages if m['role'] == 'assistant'), '')
                        
                        if not user_msg or not ai_msg:
                            validation['errors'].append(f"Item {i}: empty user or assistant message")
                            continue
                        
                        total_msg_len += len(user_msg)
                        total_resp_len += len(ai_msg)
                        
                    elif format_type in ['csv', 'jsonl']:
                        user_msg = item.get('user_message', '')
                        ai_msg = item.get('ai_response', '')
                        
                        if not user_msg or not ai_msg:
                            validation['errors'].append(f"Item {i}: empty message fields")
                            continue
                        
                        total_msg_len += len(user_msg)
                        total_resp_len += len(ai_msg)
                    
                    valid_count += 1
                    
                except Exception as e:
                    validation['errors'].append(f"Item {i}: validation error - {str(e)}")
            
            validation['stats']['valid_samples'] = valid_count
            
            if valid_count > 0:
                validation['stats']['avg_message_length'] = total_msg_len / valid_count
                validation['stats']['avg_response_length'] = total_resp_len / valid_count
            
            # Determinar se é válido
            if len(validation['errors']) > len(formatted_data) * 0.1:  # Mais de 10% de erros
                validation['is_valid'] = False
                validation['warnings'].append("Alto número de erros no dataset")
            
            if valid_count < 10:
                validation['warnings'].append("Poucos exemplos válidos para fine-tuning eficaz")
            
        except Exception as e:
            validation['is_valid'] = False
            validation['errors'].append(f"Erro na validação: {str(e)}")
        
        return validation
    
    def _generate_dataset_metadata(self, conversations: List[Dict], format_type: str, 
                                 validation: Dict, source: str = 'conversations') -> Dict:
        """Gera metadados do dataset"""
        
        metadata = {
            'creation_date': datetime.utcnow().isoformat(),
            'format': format_type,
            'source': source,
            'total_samples': len(conversations),
            'valid_samples': validation['stats']['valid_samples'],
            'quality_distribution': {},
            'risk_distribution': {},
            'avg_lengths': {
                'user_message': validation['stats']['avg_message_length'],
                'ai_response': validation['stats']['avg_response_length']
            },
            'dataset_hash': self._calculate_dataset_hash(conversations)
        }
        
        # Distribuição por qualidade
        if conversations:
            ratings = [conv.get('user_rating', 3) for conv in conversations]
            metadata['quality_distribution'] = {
                'avg_rating': sum(ratings) / len(ratings),
                'rating_counts': {str(i): ratings.count(i) for i in range(1, 6)}
            }
            
            # Distribuição por risco
            risk_levels = [conv.get('risk_level', 'low') for conv in conversations]
            metadata['risk_distribution'] = {
                level: risk_levels.count(level) 
                for level in ['low', 'moderate', 'high', 'critical']
            }
        
        return metadata
    
    def _calculate_dataset_hash(self, conversations: List[Dict]) -> str:
        """Calcula hash único do dataset para versionamento"""
        
        # Criar string representativa do dataset
        dataset_str = ""
        for conv in conversations[:100]:  # Primeiras 100 para performance
            dataset_str += conv.get('user_message', '')[:50]
            dataset_str += conv.get('ai_response', '')[:50]
        
        return hashlib.md5(dataset_str.encode()).hexdigest()
    
    def save_dataset_to_file(self, dataset_result: Dict, file_path: str = None) -> Dict:
        """Salva dataset em arquivo"""
        
        try:
            if not dataset_result.get('success', False):
                return {'success': False, 'error': 'Dataset inválido'}
            
            # Determinar caminho do arquivo
            if not file_path:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                format_type = dataset_result.get('format', 'jsonl')
                file_path = f"datasets/finetuning_{format_type}_{timestamp}.jsonl"
            
            # Criar diretório se não existir
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Salvar dados
            data = dataset_result['data']
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\\n')
            
            # Salvar metadados
            metadata_path = file_path.replace('.jsonl', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(dataset_result.get('metadata', {}), f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'file_path': file_path,
                'metadata_path': metadata_path,
                'samples_saved': len(data)
            }
            
        except Exception as e:
            logger.error(f"Erro ao salvar dataset: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_dataset_recommendations(self) -> Dict:
        """Fornece recomendações para criação de datasets"""
        
        try:
            # Analisar dados disponíveis
            conversation_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN user_rating >= 4 THEN 1 END) as quality_sessions,
                    COUNT(CASE WHEN user_rating >= 4 AND created_at >= NOW() - INTERVAL '6 months' THEN 1 END) as recent_quality,
                    AVG(user_rating) as avg_rating
                FROM chat_sessions 
                WHERE user_rating IS NOT NULL
            """)).fetchone()
            
            training_stats = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_training,
                    COUNT(CASE WHEN status = 'APPROVED' THEN 1 END) as approved_training,
                    AVG(LENGTH(content)) as avg_content_length
                FROM training_data
            """)).fetchone()
            
            conv_stats = dict(conversation_stats._mapping) if conversation_stats else {}
            train_stats = dict(training_stats._mapping) if training_stats else {}
            
            recommendations = {
                'data_availability': {
                    'conversations': conv_stats,
                    'training_data': train_stats
                },
                'recommendations': []
            }
            
            # Gerar recomendações
            quality_convs = conv_stats.get('quality_sessions', 0)
            approved_training = train_stats.get('approved_training', 0)
            
            if quality_convs >= 100:
                recommendations['recommendations'].append({
                    'type': 'conversation_dataset',
                    'priority': 'high',
                    'description': f'Criar dataset de {quality_convs} conversas de qualidade',
                    'estimated_samples': min(quality_convs, 1000)
                })
            
            if approved_training >= 10:
                recommendations['recommendations'].append({
                    'type': 'training_dataset',
                    'priority': 'medium',
                    'description': f'Criar dataset de {approved_training} dados de treinamento',
                    'estimated_samples': approved_training * 3  # Múltiplas perguntas por dado
                })
            
            if quality_convs >= 50 and approved_training >= 5:
                recommendations['recommendations'].append({
                    'type': 'hybrid_dataset',
                    'priority': 'high',
                    'description': 'Criar dataset híbrido combinando conversas e treinamento',
                    'estimated_samples': min(1500, quality_convs + approved_training * 3)
                })
            
            if not recommendations['recommendations']:
                recommendations['recommendations'].append({
                    'type': 'insufficient_data',
                    'priority': 'low',
                    'description': 'Dados insuficientes para fine-tuning de qualidade',
                    'suggestion': 'Coletar mais conversas bem avaliadas ou dados de treinamento'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro nas recomendações: {e}")
            return {'error': str(e)}


# Instância global
finetuning_preparator = FinetuningDatasetPreparator()