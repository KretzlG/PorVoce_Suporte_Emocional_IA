"""
Modelo de usuário do sistema ForYou
"""

from enum import Enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from .base import BaseModel


class UserRole(Enum):
    """Tipos de usuário no sistema"""
    ADMIN = "admin"
    CLIENT = "client" 
    VOLUNTEER = "volunteer"
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value.title()) for choice in cls]


class User(BaseModel, UserMixin):
    def get_full_name(self):
        """Compatível com o template: retorna o nome completo do usuário"""
        return self.full_name
    """
    Modelo de usuário principal do sistema
    """
    __tablename__ = 'users'
    
    # Informações básicas
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Perfil
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    
    # Tipo de usuário e status
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Controle de acesso
    last_login = db.Column(db.DateTime, nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # Conformidade LGPD/GDPR
    terms_accepted = db.Column(db.Boolean, default=False, nullable=False)
    terms_accepted_at = db.Column(db.DateTime, nullable=True)
    privacy_policy_accepted = db.Column(db.Boolean, default=False, nullable=False)
    privacy_policy_accepted_at = db.Column(db.DateTime, nullable=True)
    data_processing_consent = db.Column(db.Boolean, default=False, nullable=False)
    data_processing_consent_at = db.Column(db.DateTime, nullable=True)
    
    # Anonimização
    is_anonymized = db.Column(db.Boolean, default=False, nullable=False)
    anonymized_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    diary_entries = db.relationship('DiaryEntry', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    triage_logs = db.relationship('TriageLog', foreign_keys='TriageLog.user_id', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Relacionamento com voluntário (1:1)
    volunteer_profile = db.relationship('Volunteer', foreign_keys='Volunteer.user_id', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Define a senha do usuário (hash)"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retorna o ID do usuário para Flask-Login"""
        return str(self.id)
    
    @property
    def full_name(self):
        """Retorna nome completo"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_client(self):
        """Verifica se o usuário é cliente"""
        return self.role == UserRole.CLIENT
    
    @property
    def is_volunteer(self):
        """Verifica se o usuário é voluntário"""
        return self.role == UserRole.VOLUNTEER
    
    @property
    def is_locked(self):
        """Verifica se a conta está bloqueada"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Bloqueia a conta por um período"""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.save()
    
    def unlock_account(self):
        """Desbloqueia a conta"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save()
    
    def record_login_attempt(self, success=True):
        """Registra tentativa de login"""
        if success:
            self.last_login = datetime.utcnow()
            self.failed_login_attempts = 0
            self.locked_until = None
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 5:
                self.lock_account()
        self.save()
    
    def anonymize_data(self):
        """Anonimiza dados pessoais do usuário"""
        if self.is_anonymized:
            return
            
        # Anonimizar dados pessoais
        self.email = f"anonymous_{self.id}@anonymized.local"
        self.username = f"anonymous_user_{self.id}"
        self.first_name = "Anônimo"
        self.last_name = "Usuário"
        self.phone = None
        self.birth_date = None
        
        # Marcar como anonimizado
        self.is_anonymized = True
        self.anonymized_at = datetime.utcnow()
        
        self.save()
    
    def can_access_feature(self, feature):
        """Verifica se o usuário pode acessar uma funcionalidade"""
        if not self.is_active or self.is_locked:
            return False
            
        permissions = {
            UserRole.ADMIN: ['all'],
            UserRole.CLIENT: ['chat', 'diary', 'profile'],
            UserRole.VOLUNTEER: ['chat', 'volunteer_dashboard', 'client_support', 'profile']
        }
        
        user_permissions = permissions.get(self.role, [])
        return 'all' in user_permissions or feature in user_permissions
    
    def to_dict(self, include_sensitive=False):
        """Converte para dicionário, opcionalmente incluindo dados sensíveis"""
        data = {
            'id': self.id,
            'email': self.email if include_sensitive else '***@***.***',
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_anonymized': self.is_anonymized
        }
        
        if include_sensitive:
            data.update({
                'phone': self.phone,
                'birth_date': self.birth_date.isoformat() if self.birth_date else None,
                'terms_accepted': self.terms_accepted,
                'privacy_policy_accepted': self.privacy_policy_accepted,
                'data_processing_consent': self.data_processing_consent
            })
        
        return data
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
