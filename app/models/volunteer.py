"""
Modelos para o sistema de voluntários
"""

from enum import Enum
from datetime import datetime, time
from app import db
from .base import BaseModel


class VolunteerStatus(Enum):
    """Status do voluntário"""
    PENDING = "pending"      # Aguardando aprovação
    ACTIVE = "active"        # Ativo e disponível
    INACTIVE = "inactive"    # Temporariamente inativo
    SUSPENDED = "suspended"  # Suspenso por violação
    BLOCKED = "blocked"      # Bloqueado permanentemente


class SkillLevel(Enum):
    """Nível de habilidade"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class DayOfWeek(Enum):
    """Dias da semana"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Volunteer(BaseModel):
    """
    Perfil do voluntário
    """
    __tablename__ = 'volunteers'
    
    # Relacionamento com usuário (1:1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Informações profissionais
    profession = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(200), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    education = db.Column(db.Text, nullable=True)  # JSON com formação
    certifications = db.Column(db.Text, nullable=True)  # JSON com certificações
    
    # Status e aprovação
    status = db.Column(db.Enum(VolunteerStatus), default=VolunteerStatus.PENDING, nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Disponibilidade
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    max_concurrent_chats = db.Column(db.Integer, default=3, nullable=False)
    current_active_chats = db.Column(db.Integer, default=0, nullable=False)
    
    # Estatísticas
    total_chats = db.Column(db.Integer, default=0, nullable=False)
    total_hours = db.Column(db.Float, default=0.0, nullable=False)
    average_rating = db.Column(db.Float, nullable=True)
    total_ratings = db.Column(db.Integer, default=0, nullable=False)
    
    # Configurações
    auto_assign = db.Column(db.Boolean, default=True, nullable=False)  # Aceita atribuições automáticas
    emergency_contact = db.Column(db.Boolean, default=False, nullable=False)  # Pode ser contatado em emergências
    
    # Observações administrativas
    admin_notes = db.Column(db.Text, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    skills = db.relationship('VolunteerSkill', backref='volunteer', lazy='dynamic', cascade='all, delete-orphan')
    availability = db.relationship('VolunteerAvailability', backref='volunteer', lazy='dynamic', cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='volunteer', lazy='dynamic')
    
    @property
    def is_active(self):
        """Verifica se o voluntário está ativo"""
        return self.status == VolunteerStatus.ACTIVE
    
    @property
    def can_accept_new_chat(self):
        """Verifica se pode aceitar novos chats"""
        return (self.is_active and 
                self.is_available and 
                self.current_active_chats < self.max_concurrent_chats)
    
    @property
    def skill_list(self):
        """Lista de habilidades como strings"""
        return [skill.skill_name for skill in self.skills]
    
    def add_skill(self, skill_name, level=SkillLevel.INTERMEDIATE):
        """Adiciona uma habilidade"""
        existing = self.skills.filter_by(skill_name=skill_name).first()
        if existing:
            existing.level = level
            existing.save()
        else:
            skill = VolunteerSkill(
                volunteer_id=self.id,
                skill_name=skill_name,
                level=level
            )
            skill.save()
    
    def remove_skill(self, skill_name):
        """Remove uma habilidade"""
        skill = self.skills.filter_by(skill_name=skill_name).first()
        if skill:
            skill.delete()
    
    def set_availability(self, day_of_week, start_time, end_time):
        """Define disponibilidade para um dia"""
        availability = self.availability.filter_by(day_of_week=day_of_week).first()
        if availability:
            availability.start_time = start_time
            availability.end_time = end_time
            availability.save()
        else:
            availability = VolunteerAvailability(
                volunteer_id=self.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time
            )
            availability.save()
    
    def is_available_now(self):
        """Verifica se está disponível no momento atual"""
        if not self.can_accept_new_chat:
            return False
        
        now = datetime.now()
        current_day = now.weekday()
        current_time = now.time()
        
        # Verificar disponibilidade do dia
        day_availability = self.availability.filter_by(day_of_week=current_day).first()
        if not day_availability:
            return False
        
        return day_availability.start_time <= current_time <= day_availability.end_time
    
    def approve(self, admin_user_id):
        """Aprova o voluntário"""
        self.status = VolunteerStatus.ACTIVE
        self.approved_by = admin_user_id
        self.approved_at = datetime.utcnow()
        self.rejection_reason = None
        self.save()
    
    def reject(self, reason, admin_user_id):
        """Rejeita candidatura do voluntário"""
        self.status = VolunteerStatus.SUSPENDED
        self.rejection_reason = reason
        self.approved_by = admin_user_id
        self.save()
    
    def suspend(self, reason, admin_user_id):
        """Suspende o voluntário"""
        self.status = VolunteerStatus.SUSPENDED
        self.rejection_reason = reason
        self.is_available = False
        self.admin_notes = f"{self.admin_notes or ''}\n[{datetime.utcnow()}] Suspenso: {reason}"
        self.save()
    
    def reactivate(self, admin_user_id):
        """Reativa o voluntário"""
        self.status = VolunteerStatus.ACTIVE
        self.rejection_reason = None
        self.is_available = True
        self.admin_notes = f"{self.admin_notes or ''}\n[{datetime.utcnow()}] Reativado por admin {admin_user_id}"
        self.save()
    
    def update_rating(self, new_rating):
        """Atualiza avaliação média"""
        if self.total_ratings == 0:
            self.average_rating = new_rating
        else:
            total_score = (self.average_rating * self.total_ratings) + new_rating
            self.average_rating = total_score / (self.total_ratings + 1)
        
        self.total_ratings += 1
        self.save()
    
    def record_chat_completion(self, duration_minutes, rating=None):
        """Registra conclusão de chat"""
        self.total_chats += 1
        self.total_hours += duration_minutes / 60.0
        self.current_active_chats = max(0, self.current_active_chats - 1)
        
        if rating:
            self.update_rating(rating)
        
        self.last_activity = datetime.utcnow()
        self.save()
    
    def to_dict(self, include_sensitive=False):
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'profession': self.profession,
            'specialization': self.specialization,
            'experience_years': self.experience_years,
            'status': self.status.value,
            'is_available': self.is_available,
            'max_concurrent_chats': self.max_concurrent_chats,
            'current_active_chats': self.current_active_chats,
            'total_chats': self.total_chats,
            'total_hours': self.total_hours,
            'average_rating': self.average_rating,
            'total_ratings': self.total_ratings,
            'auto_assign': self.auto_assign,
            'emergency_contact': self.emergency_contact,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'created_at': self.created_at.isoformat(),
            'skills': [skill.to_dict() for skill in self.skills],
            'availability': [avail.to_dict() for avail in self.availability]
        }
        
        if include_sensitive:
            data.update({
                'education': self.education,
                'certifications': self.certifications,
                'admin_notes': self.admin_notes,
                'rejection_reason': self.rejection_reason
            })
        
        return data
    
    def __repr__(self):
        return f"<Volunteer {self.id} - {self.status.value}>"


class VolunteerSkill(BaseModel):
    """
    Habilidades do voluntário
    """
    __tablename__ = 'volunteer_skills'
    
    # Relacionamentos
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=False)
    
    # Habilidade
    skill_name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Enum(SkillLevel), default=SkillLevel.INTERMEDIATE, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Verificação
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # Constraint de unicidade
    __table_args__ = (
        db.UniqueConstraint('volunteer_id', 'skill_name', name='unique_volunteer_skill'),
    )
    
    def verify(self, admin_user_id):
        """Verifica a habilidade"""
        self.is_verified = True
        self.verified_by = admin_user_id
        self.verified_at = datetime.utcnow()
        self.save()
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'level': self.level.value,
            'description': self.description,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None
        }
    
    def __repr__(self):
        return f"<VolunteerSkill {self.skill_name} - {self.level.value}>"


class VolunteerAvailability(BaseModel):
    """
    Disponibilidade do voluntário por dia da semana
    """
    __tablename__ = 'volunteer_availability'
    
    # Relacionamentos
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=False)
    
    # Disponibilidade
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (Monday-Sunday)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    
    # Configurações especiais
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.String(200), nullable=True)
    
    # Constraint de unicidade
    __table_args__ = (
        db.UniqueConstraint('volunteer_id', 'day_of_week', name='unique_volunteer_day'),
    )
    
    @property
    def day_name(self):
        """Nome do dia da semana"""
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return days[self.day_of_week]
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'day_name': self.day_name,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'is_active': self.is_active,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f"<VolunteerAvailability {self.day_name} {self.start_time}-{self.end_time}>"
