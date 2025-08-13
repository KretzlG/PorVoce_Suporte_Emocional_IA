"""
Modelo para entradas do diário
"""

from enum import Enum
from datetime import datetime
from app import db
from .base import BaseModel


class MoodLevel(Enum):
    """Níveis de humor"""
    VERY_SAD = 1
    SAD = 2
    NEUTRAL = 3
    HAPPY = 4
    VERY_HAPPY = 5
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace('_', ' ').title()) for choice in cls]


class DiaryEntry(BaseModel):
    """
    Entrada do diário pessoal do usuário
    """
    __tablename__ = 'diary_entries'
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Conteúdo da entrada
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    
    # Estado emocional
    mood_level = db.Column(db.Integer, nullable=True)  # 1-5
    emotions = db.Column(db.Text, nullable=True)  # JSON com emoções identificadas
    
    # Análise automática
    sentiment_score = db.Column(db.Float, nullable=True)  # -1 a 1
    risk_level = db.Column(db.String(20), nullable=True)  # low, moderate, high, critical
    risk_factors = db.Column(db.Text, nullable=True)  # JSON com fatores de risco
    keywords = db.Column(db.Text, nullable=True)  # JSON com palavras-chave identificadas
    
    # Configurações de privacidade
    is_private = db.Column(db.Boolean, default=True, nullable=False)
    visible_to_volunteers = db.Column(db.Boolean, default=False, nullable=False)
    
    # Metadados
    word_count = db.Column(db.Integer, default=0)
    reading_time_minutes = db.Column(db.Integer, default=1)
    
    # Anonimização
    is_anonymized = db.Column(db.Boolean, default=False, nullable=False)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.content:
            self.calculate_metadata()
    
    def calculate_metadata(self):
        """Calcula metadados da entrada"""
        if self.content:
            words = len(self.content.split())
            self.word_count = words
            # Estimativa de 200 palavras por minuto
            self.reading_time_minutes = max(1, words // 200)
    
    @property
    def mood_description(self):
        """Retorna descrição do humor"""
        if not self.mood_level:
            return "Não informado"
        
        mood_map = {
            1: "Muito triste",
            2: "Triste", 
            3: "Neutro",
            4: "Feliz",
            5: "Muito feliz"
        }
        return mood_map.get(self.mood_level, "Desconhecido")
    
    @property
    def is_high_risk(self):
        """Verifica se a entrada indica alto risco"""
        return self.risk_level in ['high', 'critical']
    
    def analyze_content(self):
        """Analisa conteúdo da entrada (placeholder para IA)"""
        # Este método seria integrado com o serviço de IA
        # Por agora, apenas calcula metadados básicos
        self.calculate_metadata()
        
        # Análise básica de sentimento (placeholder)
        negative_words = ['triste', 'deprimido', 'ansioso', 'medo', 'solidão', 'dor']
        positive_words = ['feliz', 'alegre', 'grato', 'esperança', 'amor', 'paz']
        
        content_lower = self.content.lower()
        negative_count = sum(1 for word in negative_words if word in content_lower)
        positive_count = sum(1 for word in positive_words if word in content_lower)
        
        if negative_count > positive_count + 2:
            self.sentiment_score = -0.5
            self.risk_level = 'moderate'
        elif positive_count > negative_count + 2:
            self.sentiment_score = 0.5
            self.risk_level = 'low'
        else:
            self.sentiment_score = 0.0
            self.risk_level = 'low'
    
    def set_mood(self, mood_value):
        """Define o humor da entrada"""
        if isinstance(mood_value, MoodLevel):
            self.mood_level = mood_value.value
        elif isinstance(mood_value, int) and 1 <= mood_value <= 5:
            self.mood_level = mood_value
        else:
            raise ValueError("Humor deve ser um valor entre 1 e 5")
    
    def anonymize_data(self):
        """Anonimiza dados da entrada"""
        if self.is_anonymized:
            return
        
        # Remover conteúdo pessoal
        self.title = "Entrada Anônima"
        self.content = "[Conteúdo removido por privacidade]"
        
        # Manter apenas dados estatísticos
        # mood_level, sentiment_score, risk_level podem ser mantidos para análise
        
        self.is_anonymized = True
        self.anonymized_at = datetime.utcnow()
        self.save()
    
    def can_be_viewed_by(self, user):
        """Verifica se um usuário pode visualizar esta entrada"""
        # Próprio usuário sempre pode ver
        if user.id == self.user_id:
            return True
        
        # Admin pode ver todas (para moderação)
        if user.is_admin:
            return True
        
        # Voluntários podem ver se permitido e não é privada
        if user.is_volunteer and self.visible_to_volunteers and not self.is_private:
            return True
        
        return False
    
    def to_dict(self, include_content=True):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'mood_level': self.mood_level,
            'mood_description': self.mood_description,
            'sentiment_score': self.sentiment_score,
            'risk_level': self.risk_level,
            'is_private': self.is_private,
            'visible_to_volunteers': self.visible_to_volunteers,
            'word_count': self.word_count,
            'reading_time_minutes': self.reading_time_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_anonymized': self.is_anonymized
        }
        
        if include_content and not self.is_anonymized:
            data['content'] = self.content
        
        return data
    
    def __repr__(self):
        return f"<DiaryEntry {self.id} - {self.title or 'Sem título'}>"
