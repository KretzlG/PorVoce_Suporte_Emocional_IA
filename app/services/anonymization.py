"""
Serviço de anonimização de dados para conformidade LGPD/GDPR
"""

import hashlib
import random
import string
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from faker import Faker


class DataAnonymizer:
    """Classe responsável por anonimizar dados pessoais sensíveis"""
    
    def __init__(self):
        self.faker = Faker('pt_BR')  # Fake data em português brasileiro
        self._hash_salt = "foryou_anonymization_salt_2024"
    
    def anonymize_email(self, email: str) -> str:
        """
        Anonimiza email mantendo domínio genérico
        exemplo@gmail.com -> usuario_HASH@email.com
        """
        if not email or '@' not in email:
            return "usuario_anonimo@email.com"
        
        local_part, domain = email.split('@', 1)
        hash_suffix = self._generate_hash(email)[:8]
        return f"usuario_{hash_suffix}@email.com"
    
    def anonymize_name(self, name: str) -> str:
        """
        Anonimiza nome mantendo estrutura similar
        """
        if not name:
            return "Nome Anônimo"
        
        # Manter estrutura de nome e sobrenome
        parts = name.strip().split()
        if len(parts) == 1:
            return "Usuário"
        elif len(parts) == 2:
            return f"Usuário {chr(65 + len(parts[1]) % 26)}"
        else:
            return f"Usuário {chr(65 + len(' '.join(parts[1:])) % 26)}"
    
    def anonymize_phone(self, phone: str) -> str:
        """
        Anonimiza telefone mantendo formato brasileiro
        """
        if not phone:
            return "(11) 9****-****"
        
        # Manter apenas os últimos 4 dígitos
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            last_four = digits[-4:]
            return f"(11) 9****-{last_four}"
        return "(11) 9****-****"
    
    def anonymize_text_content(self, text: str, preserve_sentiment: bool = True) -> str:
        """
        Anonimiza conteúdo de texto removendo informações pessoais
        mas preservando contexto emocional se especificado
        """
        if not text:
            return ""
        
        # Remover emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '[EMAIL_REMOVIDO]', text)
        
        # Remover telefones
        text = re.sub(r'\b\d{2,3}[-\s]?\d{4,5}[-\s]?\d{4}\b', 
                     '[TELEFONE_REMOVIDO]', text)
        
        # Remover CPFs
        text = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2}\b', 
                     '[CPF_REMOVIDO]', text)
        
        # Remover endereços (padrão brasileiro básico)
        text = re.sub(r'\b[Rr]ua\s+[^,\n]+,?\s*\d+', '[ENDEREÇO_REMOVIDO]', text)
        text = re.sub(r'\b[Aa]venida\s+[^,\n]+,?\s*\d+', '[ENDEREÇO_REMOVIDO]', text)
        
        # Remover nomes próprios (heurística simples)
        if not preserve_sentiment:
            # Substituir palavras capitalizadas que podem ser nomes
            text = re.sub(r'\b[A-Z][a-z]{2,}\b', '[NOME]', text)
        
        return text
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonimiza dados completos de um usuário
        """
        anonymized = user_data.copy()
        
        # Dados pessoais identificáveis
        if 'email' in anonymized:
            anonymized['email'] = self.anonymize_email(anonymized['email'])
        
        if 'username' in anonymized:
            anonymized['username'] = f"user_{self._generate_hash(str(user_data.get('id', '')))[:8]}"
        
        if 'first_name' in anonymized:
            anonymized['first_name'] = self.anonymize_name(anonymized['first_name'])
        
        if 'last_name' in anonymized:
            anonymized['last_name'] = self.anonymize_name(anonymized['last_name'])
        
        if 'phone' in anonymized:
            anonymized['phone'] = self.anonymize_phone(anonymized['phone'])
        
        # Dados temporais - adicionar ruído para quebrar padrões
        if 'birth_date' in anonymized and anonymized['birth_date']:
            anonymized['birth_date'] = self._add_date_noise(anonymized['birth_date'])
        
        # Manter dados não-identificáveis
        non_sensitive_fields = [
            'id', 'is_active', 'profile_completed', 'privacy_consent',
            'created_at', 'updated_at', 'last_seen'
        ]
        
        return anonymized
    
    def anonymize_chat_data(self, chat_data: Dict[str, Any], preserve_sentiment: bool = True) -> Dict[str, Any]:
        """
        Anonimiza dados de chat preservando contexto emocional
        """
        anonymized = chat_data.copy()
        
        if 'content' in anonymized:
            anonymized['content'] = self.anonymize_text_content(
                anonymized['content'], preserve_sentiment
            )
        
        # Manter metadados analíticos importantes
        analytical_fields = [
            'sentiment', 'emotion', 'crisis_score', 'risk_level',
            'word_count', 'message_type', 'session_type'
        ]
        
        return anonymized
    
    def anonymize_diary_data(self, diary_data: Dict[str, Any], preserve_sentiment: bool = True) -> Dict[str, Any]:
        """
        Anonimiza dados do diário emocional
        """
        anonymized = diary_data.copy()
        
        if 'content' in anonymized:
            anonymized['content'] = self.anonymize_text_content(
                anonymized['content'], preserve_sentiment
            )
        
        if 'title' in anonymized:
            anonymized['title'] = self.anonymize_text_content(
                anonymized['title'], preserve_sentiment
            )
        
        # Manter dados analíticos importantes para pesquisa
        analytical_fields = [
            'mood_score', 'sentiment', 'primary_emotion', 'emotion_scores',
            'stress_level', 'sleep_quality', 'energy_level', 'risk_score'
        ]
        
        return anonymized
    
    def create_research_dataset(self, data_list: List[Dict[str, Any]], 
                               data_type: str = 'general') -> List[Dict[str, Any]]:
        """
        Cria dataset anonimizado para pesquisa científica
        """
        anonymized_dataset = []
        
        for item in data_list:
            if data_type == 'user':
                anonymized = self.anonymize_user_data(item)
            elif data_type == 'chat':
                anonymized = self.anonymize_chat_data(item, preserve_sentiment=True)
            elif data_type == 'diary':
                anonymized = self.anonymize_diary_data(item, preserve_sentiment=True)
            else:
                anonymized = item.copy()
            
            # Adicionar ID único para dataset
            anonymized['dataset_id'] = self._generate_hash(str(item.get('id', '')))[0:16]
            
            # Remover ID original
            if 'id' in anonymized:
                del anonymized['id']
                
            anonymized_dataset.append(anonymized)
        
        return anonymized_dataset
    
    def _generate_hash(self, data: str) -> str:
        """Gera hash consistente para os dados"""
        return hashlib.sha256(f"{data}{self._hash_salt}".encode()).hexdigest()
    
    def _add_date_noise(self, date_value, max_days: int = 30) -> str:
        """Adiciona ruído a datas para quebrar padrões temporais"""
        if isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except:
                return date_value
        else:
            date_obj = date_value
        
        # Adicionar ruído de ±max_days
        noise_days = random.randint(-max_days, max_days)
        noisy_date = date_obj + timedelta(days=noise_days)
        
        return noisy_date.isoformat()
    
    def verify_anonymization(self, original_data: Dict[str, Any], 
                           anonymized_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Verifica se a anonimização foi aplicada corretamente
        """
        verification = {
            'email_anonymized': False,
            'name_anonymized': False,
            'phone_anonymized': False,
            'content_anonymized': False,
            'preserves_analytics': True
        }
        
        # Verificar email
        if 'email' in original_data and 'email' in anonymized_data:
            verification['email_anonymized'] = (
                original_data['email'] != anonymized_data['email']
            )
        
        # Verificar nomes
        name_fields = ['first_name', 'last_name', 'username']
        name_changed = False
        for field in name_fields:
            if field in original_data and field in anonymized_data:
                if original_data[field] != anonymized_data[field]:
                    name_changed = True
                    break
        verification['name_anonymized'] = name_changed
        
        # Verificar telefone
        if 'phone' in original_data and 'phone' in anonymized_data:
            verification['phone_anonymized'] = (
                original_data['phone'] != anonymized_data['phone']
            )
        
        # Verificar conteúdo
        content_fields = ['content', 'title']
        content_changed = False
        for field in content_fields:
            if field in original_data and field in anonymized_data:
                if original_data[field] != anonymized_data[field]:
                    content_changed = True
                    break
        verification['content_anonymized'] = content_changed
        
        return verification


# Instância global do anonimizador
anonymizer = DataAnonymizer()
