"""
Modelos para chat 1a1 voluntário-cliente
"""
from datetime import datetime, timezone
from app import db

class Chat1a1Session(db.Model):
    __tablename__ = 'chat1a1_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=True)  # Nullable para casos em espera
    started_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)  # ACTIVE, WAITING, WAITING_PRIORITY, COMPLETED
    title = db.Column(db.String(200), nullable=True)
    message_count = db.Column(db.Integer, default=0)
    priority_level = db.Column(db.String(20), default='normal', nullable=False)  # normal, high, critical
    
    # Relacionamentos
    messages = db.relationship('Chat1a1Message', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='chat1a1_sessions_as_user')
    volunteer = db.relationship('Volunteer', backref='chat1a1_sessions_as_volunteer')

class Chat1a1Message(db.Model):
    __tablename__ = 'chat1a1_messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat1a1_sessions.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), nullable=False) # 'volunteer' ou 'client'
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relacionamentos
    sender = db.relationship('User', backref='chat1a1_messages_sent')
