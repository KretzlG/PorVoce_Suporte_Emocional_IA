"""
Modelos para logs administrativos
"""

from enum import Enum
from datetime import datetime
from app import db
from .base import BaseModel


class AdminAction(Enum):
    """Tipos de ações administrativas"""
    # Gestão de usuários
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    USER_ROLE_CHANGED = "user_role_changed"
    
    # Gestão de voluntários
    VOLUNTEER_APPROVED = "volunteer_approved"
    VOLUNTEER_REJECTED = "volunteer_rejected"
    VOLUNTEER_SUSPENDED = "volunteer_suspended"
    VOLUNTEER_REACTIVATED = "volunteer_reactivated"
    
    # Moderação de conteúdo
    CONTENT_MODERATED = "content_moderated"
    CONTENT_REMOVED = "content_removed"
    CONTENT_FLAGGED = "content_flagged"
    
    # Análise de risco
    RISK_REVIEW = "risk_review"
    EMERGENCY_ESCALATION = "emergency_escalation"
    MANUAL_INTERVENTION = "manual_intervention"
    
    # Configurações do sistema
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    DATABASE_MAINTENANCE = "database_maintenance"
    DATA_EXPORT = "data_export"
    DATA_ANONYMIZATION = "data_anonymization"
    
    # Auditoria e compliance
    AUDIT_PERFORMED = "audit_performed"
    GDPR_REQUEST = "gdpr_request"
    DATA_BREACH_RESPONSE = "data_breach_response"
    
    # Autenticação e segurança
    LOGIN_ATTEMPT = "login_attempt"
    PASSWORD_RESET = "password_reset"
    SECURITY_INCIDENT = "security_incident"


class LogLevel(Enum):
    """Níveis de log"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AdminLog(BaseModel):
    """
    Log de ações administrativas e auditoria
    """
    __tablename__ = 'admin_logs'
    
    # Usuário que executou a ação
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Ação executada
    action = db.Column(db.Enum(AdminAction), nullable=False)
    level = db.Column(db.Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    
    # Detalhes da ação
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, nullable=True)  # JSON com detalhes extras
    
    # Contexto da ação
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    target_type = db.Column(db.String(50), nullable=True)  # 'user', 'chat', 'diary', etc.
    target_id = db.Column(db.Integer, nullable=True)
    
    # Metadados da requisição
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    
    # Resultado da ação
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    # Dados antes/depois (para auditoria)
    before_state = db.Column(db.Text, nullable=True)  # JSON
    after_state = db.Column(db.Text, nullable=True)   # JSON
    
    # Relacionamentos
    admin_user = db.relationship('User', foreign_keys=[admin_user_id], backref='admin_actions_performed')
    target_user = db.relationship('User', foreign_keys=[target_user_id], backref='admin_actions_received')
    
    @classmethod
    def log_action(cls, admin_user_id, action, description, **kwargs):
        """Cria um novo log de ação administrativa"""
        log = cls(
            admin_user_id=admin_user_id,
            action=action,
            description=description,
            level=kwargs.get('level', LogLevel.INFO),
            details=kwargs.get('details'),
            target_user_id=kwargs.get('target_user_id'),
            target_type=kwargs.get('target_type'),
            target_id=kwargs.get('target_id'),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            session_id=kwargs.get('session_id'),
            success=kwargs.get('success', True),
            error_message=kwargs.get('error_message'),
            before_state=kwargs.get('before_state'),
            after_state=kwargs.get('after_state')
        )
        log.save()
        return log
    
    @classmethod
    def log_user_action(cls, admin_user_id, action, target_user_id, description, **kwargs):
        """Log específico para ações sobre usuários"""
        return cls.log_action(
            admin_user_id=admin_user_id,
            action=action,
            description=description,
            target_user_id=target_user_id,
            target_type='user',
            **kwargs
        )
    
    @classmethod
    def log_security_incident(cls, admin_user_id, description, ip_address=None, **kwargs):
        """Log específico para incidentes de segurança"""
        return cls.log_action(
            admin_user_id=admin_user_id,
            action=AdminAction.SECURITY_INCIDENT,
            description=description,
            level=LogLevel.CRITICAL,
            ip_address=ip_address,
            **kwargs
        )
    
    @classmethod
    def log_login_attempt(cls, user_id, success, ip_address=None, user_agent=None, **kwargs):
        """Log específico para tentativas de login"""
        return cls.log_action(
            admin_user_id=user_id,
            action=AdminAction.LOGIN_ATTEMPT,
            description=f"Login {'bem-sucedido' if success else 'falhado'}",
            level=LogLevel.INFO if success else LogLevel.WARNING,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs
        )
    
    @classmethod
    def get_user_activity(cls, user_id, limit=50):
        """Obtém atividade de um usuário específico"""
        return cls.query.filter(
            db.or_(
                cls.admin_user_id == user_id,
                cls.target_user_id == user_id
            )
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_activities(cls, hours=24, limit=100):
        """Obtém atividades recentes"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(cls.created_at >= cutoff)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_security_incidents(cls, days=7):
        """Obtém incidentes de segurança recentes"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return cls.query.filter(
            cls.created_at >= cutoff,
            cls.level.in_([LogLevel.ERROR, LogLevel.CRITICAL])
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_failed_actions(cls, hours=24):
        """Obtém ações que falharam"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.created_at >= cutoff,
            cls.success == False
        ).order_by(cls.created_at.desc()).all()
    
    @property
    def level_color(self):
        """Cor associada ao nível do log"""
        colors = {
            LogLevel.INFO: "blue",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "orange", 
            LogLevel.CRITICAL: "red"
        }
        return colors.get(self.level, "gray")
    
    @property
    def action_description(self):
        """Descrição amigável da ação"""
        descriptions = {
            AdminAction.USER_CREATED: "Usuário criado",
            AdminAction.USER_UPDATED: "Usuário atualizado",
            AdminAction.USER_DELETED: "Usuário excluído",
            AdminAction.USER_ACTIVATED: "Usuário ativado",
            AdminAction.USER_DEACTIVATED: "Usuário desativado",
            AdminAction.USER_ROLE_CHANGED: "Papel do usuário alterado",
            AdminAction.VOLUNTEER_APPROVED: "Voluntário aprovado",
            AdminAction.VOLUNTEER_REJECTED: "Voluntário rejeitado",
            AdminAction.VOLUNTEER_SUSPENDED: "Voluntário suspenso",
            AdminAction.VOLUNTEER_REACTIVATED: "Voluntário reativado",
            AdminAction.CONTENT_MODERATED: "Conteúdo moderado",
            AdminAction.CONTENT_REMOVED: "Conteúdo removido",
            AdminAction.CONTENT_FLAGGED: "Conteúdo marcado",
            AdminAction.RISK_REVIEW: "Revisão de risco",
            AdminAction.EMERGENCY_ESCALATION: "Escalação de emergência",
            AdminAction.MANUAL_INTERVENTION: "Intervenção manual",
            AdminAction.SYSTEM_CONFIG_CHANGED: "Configuração alterada",
            AdminAction.DATABASE_MAINTENANCE: "Manutenção do banco",
            AdminAction.DATA_EXPORT: "Exportação de dados",
            AdminAction.DATA_ANONYMIZATION: "Anonimização de dados",
            AdminAction.AUDIT_PERFORMED: "Auditoria realizada",
            AdminAction.GDPR_REQUEST: "Solicitação GDPR",
            AdminAction.DATA_BREACH_RESPONSE: "Resposta a violação",
            AdminAction.LOGIN_ATTEMPT: "Tentativa de login",
            AdminAction.PASSWORD_RESET: "Reset de senha",
            AdminAction.SECURITY_INCIDENT: "Incidente de segurança"
        }
        return descriptions.get(self.action, self.action.value)
    
    def to_dict(self, include_sensitive=False):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'admin_user_id': self.admin_user_id,
            'action': self.action.value,
            'action_description': self.action_description,
            'level': self.level.value,
            'level_color': self.level_color,
            'description': self.description,
            'target_user_id': self.target_user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'success': self.success,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                'details': self.details,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'session_id': self.session_id,
                'error_message': self.error_message,
                'before_state': self.before_state,
                'after_state': self.after_state
            })
        
        return data
    
    def __repr__(self):
        return f"<AdminLog {self.id} - {self.action.value}>"
