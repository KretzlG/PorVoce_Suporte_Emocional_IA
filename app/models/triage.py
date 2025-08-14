"""
Modelos para logs de triagem e análise de risco
"""

from enum import Enum
from datetime import datetime
from app import db
from .base import BaseModel


class RiskLevel(Enum):
    """Níveis de risco identificados"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value.title()) for choice in cls]
    
    @classmethod
    def get_color(cls, level):
        """Retorna cor associada ao nível de risco"""
        colors = {
            cls.LOW: "green",
            cls.MODERATE: "yellow", 
            cls.HIGH: "orange",
            cls.CRITICAL: "red"
        }
        return colors.get(level, "gray")


class TriageAction(Enum):
    """Ações tomadas durante triagem"""
    MONITORED = "monitored"           # Apenas monitoramento
    ESCALATED = "escalated"           # Escalado para voluntário
    EMERGENCY_CONTACT = "emergency"   # Contato de emergência acionado
    PROFESSIONAL_REFERRAL = "referral"  # Encaminhado para profissional
    SELF_HELP_SUGGESTED = "self_help"   # Sugeridas técnicas de auto-ajuda


class TriageLog(BaseModel):
    """
    Log de triagem e análise de risco de usuários
    """
    __tablename__ = 'triage_logs'
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=True)
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=True)
    
    # Análise de risco
    risk_level = db.Column(db.Enum(RiskLevel), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)  # 0-1
    risk_factors = db.Column(db.Text, nullable=True)  # JSON com fatores identificados
    
    # Contexto da análise
    trigger_content = db.Column(db.Text, nullable=True)  # Conteúdo que disparou a análise
    context_type = db.Column(db.String(50), nullable=False)  # 'chat', 'diary', 'profile'
    
    # Indicadores específicos
    suicidal_ideation = db.Column(db.Boolean, default=False, nullable=False)
    self_harm_risk = db.Column(db.Boolean, default=False, nullable=False)
    substance_abuse = db.Column(db.Boolean, default=False, nullable=False)
    domestic_violence = db.Column(db.Boolean, default=False, nullable=False)
    severe_depression = db.Column(db.Boolean, default=False, nullable=False)
    anxiety_disorder = db.Column(db.Boolean, default=False, nullable=False)
    
    # Ações tomadas
    action_taken = db.Column(db.Enum(TriageAction), nullable=True)
    action_details = db.Column(db.Text, nullable=True)
    follow_up_required = db.Column(db.Boolean, default=False, nullable=False)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    
    # Responsável pela análise
    analyzed_by_ai = db.Column(db.Boolean, default=True, nullable=False)
    reviewed_by_human = db.Column(db.Boolean, default=False, nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    # Metadados da análise
    ai_model_used = db.Column(db.String(100), nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    keywords_detected = db.Column(db.Text, nullable=True)  # JSON
    sentiment_score = db.Column(db.Float, nullable=True)  # -1 a 1
    
    # Anonimização
    is_anonymized = db.Column(db.Boolean, default=False, nullable=False)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    @property
    def is_high_risk(self):
        """Verifica se é alto risco"""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @property
    def requires_immediate_attention(self):
        """Verifica se requer atenção imediata"""
        return (self.risk_level == RiskLevel.CRITICAL or 
                self.suicidal_ideation or 
                self.self_harm_risk)
    
    @property
    def risk_color(self):
        """Cor associada ao nível de risco"""
        return RiskLevel.get_color(self.risk_level)
    
    def add_human_review(self, reviewer_id, notes, confirmed_risk_level=None):
        """Adiciona revisão humana"""
        self.reviewed_by_human = True
        self.reviewer_id = reviewer_id
        self.review_notes = notes
        
        # Permite ajustar o nível de risco após revisão humana
        if confirmed_risk_level:
            self.risk_level = confirmed_risk_level
        
        self.save()
    
    def escalate_to_volunteer(self, volunteer_id, action_details=None):
        """Escala para voluntário"""
        self.action_taken = TriageAction.ESCALATED
        self.action_details = action_details or f"Escalado para voluntário {volunteer_id}"
        self.follow_up_required = True
        self.save()
    
    def trigger_emergency_contact(self, contact_details):
        """Aciona contato de emergência"""
        self.action_taken = TriageAction.EMERGENCY_CONTACT
        self.action_details = contact_details
        self.follow_up_required = True
        self.save()
    
    def suggest_professional_help(self, referral_info):
        """Sugere ajuda profissional"""
        self.action_taken = TriageAction.PROFESSIONAL_REFERRAL
        self.action_details = referral_info
        self.follow_up_required = True
        self.save()
    
    def anonymize_data(self):
        """Anonimiza dados do log"""
        if self.is_anonymized:
            return
        
        # Remover conteúdo sensível mas manter dados estatísticos
        self.trigger_content = "[Conteúdo removido por privacidade]"
        self.action_details = "[Detalhes removidos por privacidade]"
        self.review_notes = "[Notas removidas por privacidade]"
        self.keywords_detected = None
        
        # Manter indicadores de risco e ações para análise estatística
        
        self.is_anonymized = True
        self.anonymized_at = datetime.utcnow()
        self.save()
    
    @classmethod
    def get_user_risk_history(cls, user_id, limit=10):
        """Obtém histórico de risco do usuário"""
        return cls.query.filter_by(user_id=user_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_high_risk_cases(cls, hours=24):
        """Obtém casos de alto risco nas últimas horas"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.created_at >= cutoff,
            cls.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL])
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_unreviewed_critical_cases(cls):
        """Obtém casos críticos não revisados"""
        return cls.query.filter(
            cls.risk_level == RiskLevel.CRITICAL,
            cls.reviewed_by_human == False
        ).order_by(cls.created_at.asc()).all()
    
    def to_dict(self, include_sensitive=False):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'chat_session_id': self.chat_session_id,
            'diary_entry_id': self.diary_entry_id,
            'risk_level': self.risk_level.value,
            'confidence_score': self.confidence_score,
            'context_type': self.context_type,
            'suicidal_ideation': self.suicidal_ideation,
            'self_harm_risk': self.self_harm_risk,
            'substance_abuse': self.substance_abuse,
            'domestic_violence': self.domestic_violence,
            'severe_depression': self.severe_depression,
            'anxiety_disorder': self.anxiety_disorder,
            'action_taken': self.action_taken.value if self.action_taken else None,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'analyzed_by_ai': self.analyzed_by_ai,
            'reviewed_by_human': self.reviewed_by_human,
            'reviewer_id': self.reviewer_id,
            'ai_model_used': self.ai_model_used,
            'processing_time_ms': self.processing_time_ms,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat(),
            'is_anonymized': self.is_anonymized,
            'risk_color': self.risk_color
        }
        
        if include_sensitive and not self.is_anonymized:
            data.update({
                'trigger_content': self.trigger_content,
                'risk_factors': self.risk_factors,
                'action_details': self.action_details,
                'review_notes': self.review_notes,
                'keywords_detected': self.keywords_detected
            })
        
        return data
    
    def __repr__(self):
        return f"<TriageLog {self.id} - {self.risk_level.value} risk>"
