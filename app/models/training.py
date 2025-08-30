"""
Modelo para treinamento da IA
"""

from enum import Enum
from datetime import datetime
from app import db

from .base import BaseModel
from sqlalchemy import Text, Enum as SQLEnum
from pgvector.sqlalchemy import Vector


class TrainingDataType(Enum):
    """Tipos de dados de treinamento"""
    TEXT = "text"
    FILE = "file"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value.title()) for choice in cls]


class TrainingDataStatus(Enum):
    """Status do dado de treinamento"""
    PENDING = "pending"
    VALIDATING = "validating"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSED = "processed"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value.title()) for choice in cls]


class TrainingData(BaseModel):
    """
    Modelo para dados de treinamento da IA
    """
    __tablename__ = 'training_data'
    
    # Dados básicos
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text, nullable=True)
    content = db.Column(Text, nullable=True)  # Para texto direto
    
    # Arquivo (se for upload)
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    
    # Tipo e status
    data_type = db.Column(SQLEnum(TrainingDataType), nullable=False, default=TrainingDataType.TEXT)
    status = db.Column(SQLEnum(TrainingDataStatus), nullable=False, default=TrainingDataStatus.PENDING)
    
    # Validação
    validation_notes = db.Column(Text, nullable=True)
    validation_score = db.Column(db.Float, nullable=True)  # Score de 0 a 1
    
    # Relacionamentos
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    validated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    validated_at = db.Column(db.DateTime, nullable=True)
    
    # Metadados de processamento
    processed_at = db.Column(db.DateTime, nullable=True)
    processing_logs = db.Column(Text, nullable=True)

    # Embedding vetorial para RAG
    embedding = db.Column(Vector(1536), nullable=True, index=True, comment="Embedding para busca vetorial (RAG)")
    
    # Relacionamentos
    submitter = db.relationship('User', foreign_keys=[submitted_by], backref='submitted_trainings')
    validator = db.relationship('User', foreign_keys=[validated_by], backref='validated_trainings')
    
    def __repr__(self):
        return f'<TrainingData {self.title}>'
    
    def is_approved(self):
        """Verifica se o dado foi aprovado"""
        return self.status == TrainingDataStatus.APPROVED
    
    def is_pending(self):
        """Verifica se o dado está pendente"""
        return self.status == TrainingDataStatus.PENDING
    
    def is_rejected(self):
        """Verifica se o dado foi rejeitado"""
        return self.status == TrainingDataStatus.REJECTED
    
    def approve(self, validator_id, notes=None):
        """Aprova o dado de treinamento"""
        self.status = TrainingDataStatus.APPROVED
        self.validated_by = validator_id
        self.validated_at = datetime.utcnow()
        if notes:
            self.validation_notes = notes
        self.save()
    
    def reject(self, validator_id, notes):
        """Rejeita o dado de treinamento"""
        self.status = TrainingDataStatus.REJECTED
        self.validated_by = validator_id
        self.validated_at = datetime.utcnow()
        self.validation_notes = notes
        self.save()
    
    def mark_as_processed(self, logs=None):
        """Marca como processado pela IA"""
        self.status = TrainingDataStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        if logs:
            self.processing_logs = logs
        self.save()
    
    def get_content_preview(self, max_length=200):
        """Retorna uma prévia do conteúdo"""
        if self.content:
            return self.content[:max_length] + "..." if len(self.content) > max_length else self.content
        return "Arquivo anexado"
    
    def to_dict(self):
        """Converte para dicionário"""
        data = super().to_dict()
        data.update({
            'data_type': self.data_type.value if self.data_type else None,
            'status': self.status.value if self.status else None,
            'submitter_name': self.submitter.get_full_name() if self.submitter else None,
            'validator_name': self.validator.get_full_name() if self.validator else None,
            'content_preview': self.get_content_preview()
        })
        return data
