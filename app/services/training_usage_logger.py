"""
Sistema de Logging para Rastreamento de Uso de Dados de Treinamento
Monitora se a IA está utilizando os dados submetidos via sistema de treinamento
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import text
from app import db
from app.models import TrainingData, TrainingDataStatus, TrainingDataType
from app.models import TrainingData, TrainingDataStatus

# Configurar logger específico para treinamento
training_logger = logging.getLogger('training_usage')
training_handler = logging.FileHandler('logs/training_usage.log')
training_formatter = logging.Formatter(
    '%(asctime)s - TRAINING_USAGE - %(levelname)s - %(message)s'
)
training_handler.setFormatter(training_formatter)
training_logger.addHandler(training_handler)
training_logger.setLevel(logging.INFO)


class TrainingUsageLogger:
    """
    Logger especializado para rastrear uso de dados de treinamento
    """
    
    def __init__(self):
        self.training_data_cache = {}
        self.usage_stats = {
            'total_queries': 0,
            'training_matches': 0,
            'file_matches': 0,
            'text_matches': 0
        }
    
    def get_training_data(self) -> List[Dict]:
        """
        Recupera todos os dados de treinamento aprovados
        """
        try:
            training_data = TrainingData.query.filter_by(
                status=TrainingDataStatus.APPROVED
            ).all()
            
            print(f"TRAINING_DATA_LOAD: Carregando {len(training_data)} dados aprovados")
            
            data_list = []
            for item in training_data:
                data_dict = {
                    'id': item.id,
                    'title': item.title,
                    'description': item.description or '',
                    'data_type': item.data_type.value,
                    'content': item.content or '',
                    'file_name': item.file_name or '',
                    'file_path': item.file_path or '',
                    'file_type': item.file_type or '',
                    'keywords': self._extract_keywords(item)
                }
                data_list.append(data_dict)
            
            self.training_data_cache['training_data'] = data_list
            self.training_data_cache['last_updated'] = datetime.now()
            
            return data_list
            
        except Exception as e:
            print(f"Erro ao recuperar dados de treinamento: {e}")
            return []
    
    def _extract_keywords(self, training_item: TrainingData) -> List[str]:
        """
        Extrai palavras-chave dos dados de treinamento
        """
        text_content = f"{training_item.title} {training_item.description or ''} {training_item.content or ''}"
        
        # Se for um arquivo, tentar extrair conteúdo
        if training_item.data_type == TrainingDataType.FILE and training_item.file_path:
            try:
                file_content = self._extract_file_content(training_item.file_path, training_item.file_type)
                if file_content:
                    text_content += " " + file_content
                    print(f"FILE_EXTRACTION: Extraído {len(file_content)} caracteres do arquivo {training_item.file_name}")
                else:
                    print(f"FILE_EXTRACTION: Falha ao extrair conteúdo do arquivo {training_item.file_name}")
            except Exception as e:
                print(f"FILE_EXTRACTION: Erro ao extrair arquivo {training_item.file_name}: {str(e)}")
        
        # Palavras-chave específicas para saúde mental e suporte emocional
        priority_keywords = [
            'ansiedade', 'pânico', 'depressão', 'estresse', 'medo', 'fobia',
            'criança', 'crianças', 'adolescente', 'adolescentes', 'jovem',
            'síndrome', 'transtorno', 'crise', 'ataque', 'episódio',
            'tratamento', 'terapia', 'ajuda', 'apoio', 'suporte',
            'emocional', 'psicológico', 'mental', 'comportamental',
            'fatores', 'causas', 'sintomas', 'desenvolvimento',
            'genética', 'familiar', 'trauma', 'estressor', 'manejo',
            'clínicas', 'clínico', 'diagnóstico', 'características',
            'infância', 'hiperatividade', 'impulsividade', 'concentração',
            'desatenção', 'escolar', 'comportamento', 'desafiador'
        ]
        
        keywords = []
        words = text_content.lower().split()
        
        # Stopwords expandidas
        stopwords = {
            'que', 'para', 'com', 'uma', 'por', 'não', 'mais', 'como', 'isso', 
            'quando', 'onde', 'ser', 'ter', 'estar', 'fazer', 'dizer', 'ver',
            'dar', 'saber', 'poder', 'querer', 'ficar', 'muito', 'bem', 'já',
            'ainda', 'também', 'só', 'depois', 'sem', 'até', 'pelo', 'pela',
            'dos', 'das', 'uma', 'uns', 'umas', 'este', 'esta', 'estes', 'estas',
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after'
        }
        
        # Primeiro, adicionar todas as palavras-chave prioritárias encontradas
        for word in words:
            # Limpar pontuação
            word = word.strip('.,!?;:"()[]{}')
            
            # Priorizar palavras-chave específicas
            if word in priority_keywords:
                keywords.append(word)
        
        # Depois, adicionar palavras significativas limitadas
        significant_words = []
        for word in words:
            word = word.strip('.,!?;:"()[]{}')
            if (len(word) > 4 and word not in stopwords and 
                word.isalpha() and word not in priority_keywords):
                significant_words.append(word)
        
        # Limitar palavras significativas para evitar ruído
        significant_words = list(set(significant_words))[:50]  # Máximo 50 palavras extras
        keywords.extend(significant_words)
        
        # Log para debug
        extracted_keywords = list(set(keywords))
        print(f"KEYWORDS_EXTRACTION: Item {training_item.id} - {len(extracted_keywords)} palavras-chave: {extracted_keywords[:10]}...")
        
        return extracted_keywords
    
    def _extract_file_content(self, file_path: str, file_type: str) -> Optional[str]:
        """
        Extrai conteúdo de diferentes tipos de arquivo
        """
        try:
            if file_type.lower() in ['txt', 'text']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type.lower() == 'pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                        return text
                except ImportError:
                    print("PyPDF2 não disponível para extração de PDF")
                    return None
            
            elif file_type.lower() in ['doc', 'docx']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    print("python-docx não disponível para extração de DOC")
                    return None
            
            elif file_type.lower() == 'odt':
                try:
                    from odf import text, teletype
                    from odf.opendocument import load
                    
                    textdoc = load(file_path)
                    allparas = textdoc.getElementsByType(text.P)
                    content = ""
                    for para in allparas:
                        content += teletype.extractText(para) + "\n"
                    return content
                except ImportError:
                    print("odfpy não disponível para extração de ODT")
                    return None
            
            else:
                print(f"Tipo de arquivo não suportado: {file_type}")
                return None
                
        except Exception as e:
            print(f"Erro ao extrair conteúdo do arquivo: {str(e)}")
            return None
    
    def check_training_usage(self, user_message: str, ai_response: str, 
                           risk_level: str = 'low') -> Dict:
        """
        Verifica se a resposta da IA utilizou dados de treinamento
        """
        self.usage_stats['total_queries'] += 1
        
        try:
            training_data = self.get_training_data()
            print(f"TRAINING_DEBUG: Encontrados {len(training_data)} dados de treinamento")
            
            matches = []
            
            user_words = set(user_message.lower().split())
            response_words = set(ai_response.lower().split())
            
            for training_item in training_data:
                match_info = self._check_content_similarity(
                    user_message, ai_response, training_item, user_words, response_words
                )
                
                print(f"TRAINING_DEBUG: Training ID {training_item.get('id', 'N/A')} - Score: {match_info['similarity_score']:.3f}")
                
                if match_info['similarity_score'] > 0.05:  # Limiar ainda mais baixo para detectar mais correspondências
                    matches.append(match_info)
                    print(f"TRAINING_DEBUG: MATCH FOUND! Score: {match_info['similarity_score']:.3f}")
                    
                    # Atualizar estatísticas
                    self.usage_stats['training_matches'] += 1
                    if training_item['data_type'] == 'file':
                        self.usage_stats['file_matches'] += 1
                    else:
                        self.usage_stats['text_matches'] += 1
                    
        except Exception as e:
            print(f"Erro ao verificar uso de dados de treinamento: {str(e)}")
            matches = []
        
        # Ordenar por similaridade
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Log do resultado
        usage_result = {
            'timestamp': datetime.now().isoformat(),
            'user_message_length': len(user_message),
            'ai_response_length': len(ai_response),
            'risk_level': risk_level,
            'training_matches_found': len(matches),
            'top_matches': matches[:3],  # Apenas top 3
            'used_training_data': len(matches) > 0
        }
        
        # Log detalhado
        if matches:
            print(f"TRAINING_DATA_USED: {json.dumps(usage_result, ensure_ascii=False)}")
        else:
            print(f"NO_TRAINING_DATA_USED: Query processed without training data matches")
        
        return usage_result
    
    def _check_content_similarity(self, user_message: str, ai_response: str, 
                                training_item: Dict, user_words: set, 
                                response_words: set) -> Dict:
        """
        Verifica similaridade entre a conversa atual e um item de treinamento
        """
        try:
            # Palavras-chave prioritárias para busca
            priority_keywords = [
                'ansiedade', 'pânico', 'depressão', 'estresse', 'medo', 'fobia',
                'criança', 'crianças', 'adolescente', 'adolescentes', 'jovem',
                'síndrome', 'transtorno', 'crise', 'ataque', 'episódio',
                'tratamento', 'terapia', 'ajuda', 'apoio', 'suporte',
                'emocional', 'psicológico', 'mental', 'comportamental',
                'fatores', 'causas', 'sintomas', 'desenvolvimento',
                'genética', 'familiar', 'trauma', 'estressor', 'manejo',
                'clínicas', 'clínico', 'diagnóstico', 'características',
                'infância', 'hiperatividade', 'impulsividade', 'concentração',
                'desatenção', 'escolar', 'comportamento', 'desafiador'
            ]
            
            # Combinar texto do usuário e resposta da IA
            combined_text = f"{user_message} {ai_response}".lower()
            combined_words = set(combined_text.split())
            
            # Extrair palavras do treinamento
            training_text = f"{training_item['title']} {training_item['description']} {training_item['content']}".lower()
            training_keywords = set(training_item['keywords'])
            
            # 1. Score por palavras-chave prioritárias
            priority_matches = 0
            for keyword in priority_keywords:
                if keyword in combined_text and keyword in training_text:
                    priority_matches += 2  # Peso maior para prioridades
                    
            # 2. Score por palavras-chave gerais
            general_matches = len(combined_words.intersection(training_keywords))
            
            # 3. Score por correspondência de frases (3+ palavras)
            phrase_score = 0
            words_list = combined_text.split()
            for i in range(len(words_list) - 2):
                phrase = " ".join(words_list[i:i+3])
                if phrase in training_text:
                    phrase_score += 1
                    
            # 4. Score por correspondência direta de termos técnicos
            technical_terms = [
                "características clínicas", "infância adolescência", "sintomas",
                "diagnóstico", "tratamento", "manejo crises", "ansiedade pânico"
            ]
            
            technical_score = 0
            for term in technical_terms:
                if term in combined_text and term in training_text:
                    technical_score += 3  # Peso alto para termos técnicos
            
            # Calcular score final
            total_score = (priority_matches * 0.4) + (general_matches * 0.2) + (phrase_score * 0.2) + (technical_score * 0.2)
            
            # Normalizar baseado no tamanho do conteúdo de treinamento
            content_size_factor = min(len(training_text) / 10000, 1.0)  # Normalizar para textos grandes
            normalized_score = total_score / (100 * content_size_factor) if content_size_factor > 0 else 0
            
            print(f"SIMILARITY_DEBUG: ID {training_item['id']} - Priority: {priority_matches}, General: {general_matches}, Phrase: {phrase_score}, Technical: {technical_score}, Final: {normalized_score:.3f}")
            
            return {
                'training_id': training_item['id'],
                'training_title': training_item['title'],
                'training_type': training_item['data_type'],
                'similarity_score': round(normalized_score, 3),
                'priority_matches': priority_matches,
                'general_matches': general_matches,
                'phrase_matches': phrase_score,
                'technical_matches': technical_score,
                'details': {
                    'total_raw_score': total_score,
                    'content_size_factor': content_size_factor,
                    'matched_keywords': list(combined_words.intersection(training_keywords))[:10]
                }
            }
            
        except Exception as e:
            print(f"SIMILARITY_ERROR: {str(e)}")
            return {
                'training_id': training_item.get('id', 'unknown'),
                'similarity_score': 0,
                'error': str(e)
            }
    
    def _get_phrases(self, text: str, min_length: int = 3, max_length: int = 5) -> List[str]:
        """
        Extrai frases de tamanho específico do texto
        """
        words = text.lower().split()
        phrases = []
        
        for length in range(min_length, max_length + 1):
            for i in range(len(words) - length + 1):
                phrase = ' '.join(words[i:i+length])
                if len(phrase) > 10:  # Frases mínimas de 10 caracteres
                    phrases.append(phrase)
        
        return phrases[:20]  # Máximo 20 frases
    
    def get_usage_statistics(self) -> Dict:
        """
        Retorna estatísticas de uso dos dados de treinamento
        """
        try:
            training_data = self.get_training_data()
            
            stats = {
                'total_training_items': len(training_data),
                'file_based_items': len([t for t in training_data if t['data_type'] == 'file']),
                'text_based_items': len([t for t in training_data if t['data_type'] == 'text']),
                'usage_statistics': self.usage_stats.copy(),
                'usage_rate': {
                    'training_usage_percentage': round(
                        (self.usage_stats['training_matches'] / max(self.usage_stats['total_queries'], 1)) * 100, 2
                    ),
                    'file_usage_percentage': round(
                        (self.usage_stats['file_matches'] / max(self.usage_stats['total_queries'], 1)) * 100, 2
                    ),
                    'text_usage_percentage': round(
                        (self.usage_stats['text_matches'] / max(self.usage_stats['total_queries'], 1)) * 100, 2
                    )
                },
                'last_cache_update': self.training_data_cache.get('last_updated', 'Never').isoformat() 
                    if isinstance(self.training_data_cache.get('last_updated'), datetime) else 'Never'
            }
            
            return stats
            
        except Exception as e:
            training_logger.error(f"Erro ao gerar estatísticas: {e}")
            return {
                'error': str(e),
                'usage_statistics': self.usage_stats.copy()
            }
    
    def log_training_file_usage(self, file_path: str, extracted_content: str) -> None:
        """
        Log específico para quando arquivos de treinamento são lidos
        """
        try:
            file_info = {
                'timestamp': datetime.now().isoformat(),
                'action': 'FILE_CONTENT_EXTRACTED',
                'file_path': file_path,
                'content_length': len(extracted_content),
                'content_preview': extracted_content[:100] + '...' if len(extracted_content) > 100 else extracted_content
            }
            
            training_logger.info(f"FILE_EXTRACTION: {json.dumps(file_info, ensure_ascii=False)}")
            
        except Exception as e:
            training_logger.error(f"Erro ao logar extração de arquivo: {e}")
    
    def clear_cache(self) -> None:
        """
        Limpa o cache de dados de treinamento
        """
        self.training_data_cache.clear()
        training_logger.info("Cache de dados de treinamento limpo")


# Instância global do logger
training_usage_logger = TrainingUsageLogger()


def log_ai_response_with_training_check(user_message: str, ai_response: str, 
                                       risk_level: str = 'low') -> Dict:
    """
    Função de conveniência para logar resposta da IA e verificar uso de treinamento
    """
    return training_usage_logger.check_training_usage(user_message, ai_response, risk_level)


def get_training_usage_stats() -> Dict:
    """
    Função de conveniência para obter estatísticas
    """
    return training_usage_logger.get_usage_statistics()


def clear_training_cache() -> None:
    """
    Função de conveniência para limpar cache
    """
    training_usage_logger.clear_cache()