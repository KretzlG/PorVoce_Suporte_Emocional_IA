"""
Modelos para o sistema de chat
"""

from enum import Enum
from datetime import datetime, timezone
import uuid
from app import db
from .base import BaseModel


class ChatSessionStatus(Enum):
    """Status das sessões de chat"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    TRANSFERRED = "TRANSFERRED"  # Transferido para voluntário


class ChatMessageType(Enum):
    """Tipos de mensagem no chat"""
    USER = "user"
    AI = "ai"
    VOLUNTEER = "volunteer"
    SYSTEM = "system"


class ChatSession(BaseModel):
    def get_messages(self, limit=None, offset=0):
        """Retorna as mensagens da sessão em formato de dicionário - OTIMIZADO"""
        query = self.messages.order_by(ChatMessage.created_at.asc())
        if limit:
            query = query.limit(limit).offset(offset)
        return [msg.to_dict() for msg in query.all()]
    
    def get_recent_messages(self, limit=10):
        """Busca apenas mensagens recentes - PERFORMANCE OTIMIZADA"""
        recent = self.messages.order_by(ChatMessage.created_at.desc()).limit(limit).all()
        return [msg.to_dict() for msg in reversed(recent)]  # Ordem cronológica
    def calculate_duration(self):
        """Calcula e atualiza a duração da sessão em minutos"""
        if self.started_at and self.ended_at:
            started = self.started_at
            ended = self.ended_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            if ended.tzinfo is None:
                ended = ended.replace(tzinfo=timezone.utc)
            duration = ended - started
            self.duration_minutes = int(duration.total_seconds() / 60)
        else:
            self.duration_minutes = None
    """
    Sessão de chat entre usuário e IA/voluntário
    """
    __tablename__ = 'chat_sessions'
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=True)
    
    # Informações da sessão
    title = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Enum(ChatSessionStatus), default=ChatSessionStatus.ACTIVE.value, nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    
    # Análise de risco
    initial_risk_level = db.Column(db.String(20), nullable=True)  # low, moderate, high, critical
    final_risk_level = db.Column(db.String(20), nullable=True)
    risk_factors = db.Column(db.Text, nullable=True)  # JSON com fatores identificados
    
    # Feedback e avaliação
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5
    user_feedback = db.Column(db.Text, nullable=True)
    volunteer_notes = db.Column(db.Text, nullable=True)
    
    # Metadados
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.String(500), nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    message_count = db.Column(db.Integer, default=0)
    
    # Anonimização
    is_anonymized = db.Column(db.Boolean, default=False, nullable=False)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    # Identificador único
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    
    # Relacionamentos
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', 
                             cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    
    last_activity = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.started_at = datetime.now(timezone.utc)
    
    @property
    def is_active(self):
        """Verifica se a sessão está ativa"""
        return self.status == ChatSessionStatus.ACTIVE.value
    
    @property
    def duration(self):
        """Retorna duração da sessão"""
        if self.ended_at and self.started_at:
            return self.ended_at - self.started_at
        elif self.started_at:
            return datetime.utcnow() - self.started_at
        return None
    
    def add_message(self, content, message_type=ChatMessageType.USER, sender_id=None, message_metadata=None):
        """Adiciona uma mensagem à sessão - OTIMIZADO"""
        message = ChatMessage(
            session_id=self.id,
            content=content,
            message_type=message_type,
            sender_id=sender_id,
            message_metadata=message_metadata
        )
        
        # OTIMIZAÇÃO: Incrementar contador em vez de recontar
        self.message_count += 1
        self.last_activity = datetime.now(timezone.utc)
        
        # Adicionar à sessão sem commit automático (permite transações batch)
        db.session.add(message)
        db.session.add(self)
        
        return message
    
    def end_session(self, status=ChatSessionStatus.COMPLETED.value):
        """Finaliza a sessão"""
        self.status = status
        self.ended_at = datetime.utcnow()
        if self.started_at:
            duration = self.ended_at - self.started_at
            self.duration_minutes = int(duration.total_seconds() / 60)
        self.save()
    
    def transfer_to_volunteer(self, volunteer_id):
        """Transfere sessão para voluntário"""
        self.volunteer_id = volunteer_id
        self.status = ChatSessionStatus.TRANSFERRED.value
        self.save()
        # Adicionar mensagem do sistema
        self.add_message(
            "Sua conversa foi transferida para um voluntário especializado.",
            ChatMessageType.SYSTEM
        )
    
    def anonymize_data(self):
        """Anonimiza dados da sessão"""
        if self.is_anonymized:
            return
        
        # Anonimizar informações sensíveis
        self.title = "Sessão Anônima"
        self.ip_address = "0.0.0.0"
        self.user_agent = "Anonimizado"
        self.user_feedback = None if self.user_feedback else None
        
        # Anonimizar mensagens
        for message in self.messages:
            message.anonymize_data()
        
        self.is_anonymized = True
        self.anonymized_at = datetime.utcnow()
        self.save()
    
    def to_dict(self, include_messages=False):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.duration_minutes,
            'message_count': self.message_count,
            'initial_risk_level': self.initial_risk_level,
            'final_risk_level': self.final_risk_level,
            'user_rating': self.user_rating,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None,
            'is_anonymized': self.is_anonymized
        }
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        return data
    
    def __repr__(self):
        return f"<ChatSession {self.id} - {self.status.value}>"


class ChatMessage(BaseModel):
    """
    Mensagem individual no chat
    """
    __tablename__ = 'chat_messages'
    
    # Relacionamentos
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null para IA
    
    # Conteúdo da mensagem
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.Enum(ChatMessageType), nullable=False)
    
    # Metadados e análise
    message_metadata = db.Column(db.Text, nullable=True)  # JSON com metadados
    sentiment_score = db.Column(db.Float, nullable=True)  # -1 a 1
    risk_indicators = db.Column(db.Text, nullable=True)  # JSON com indicadores
    
    # IA Response metadata
    ai_model_used = db.Column(db.String(100), nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    
    # Anonimização
    is_anonymized = db.Column(db.Boolean, default=False, nullable=False)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    def anonymize_data(self):
        """Anonimiza conteúdo da mensagem"""
        if self.is_anonymized:
            return
        
        # Para mensagens do usuário, substituir por texto genérico
        if self.message_type == ChatMessageType.USER:
            self.content = "[Conteúdo do usuário removido por privacidade]"
        elif self.message_type == ChatMessageType.VOLUNTEER:
            self.content = "[Resposta de voluntário removida por privacidade]"
        
        # Limpar metadados sensíveis
        self.message_metadata = None
        self.risk_indicators = None
        
        self.is_anonymized = True
        self.anonymized_at = datetime.utcnow()
        self.save()
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'message_type': self.message_type.value,
            'sentiment_score': self.sentiment_score,
            'risk_indicators': self.risk_indicators,
            'ai_model_used': self.ai_model_used,
            'ai_confidence': self.ai_confidence,
            'processing_time_ms': self.processing_time_ms,
            'created_at': self.created_at.isoformat(),
            'is_anonymized': self.is_anonymized
        }
    
    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.message_type.value}>"
