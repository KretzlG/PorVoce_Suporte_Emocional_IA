"""
Modelos do banco de dados da aplicação ForYou
"""

from .user import User, UserRole
from .chat import ChatSession, ChatMessage, ChatSessionStatus, ChatMessageType
from .chat1a1 import Chat1a1Session, Chat1a1Message
from .diary import DiaryEntry, MoodLevel
from .volunteer import (
    Volunteer, VolunteerSkill, VolunteerAvailability, 
    VolunteerStatus, SkillLevel, DayOfWeek
)
from .triage import TriageLog, RiskLevel, TriageAction
from .admin import AdminLog, AdminAction, LogLevel
from .training import TrainingData, TrainingDataType, TrainingDataStatus
from .base import BaseModel

# Lista de todos os modelos para facilitar importação
__all__ = [
    'User',
    'UserRole', 
    'ChatSession',
    'ChatMessage',
    'ChatSessionStatus',
    'ChatMessageType',
    'Chat1a1Session',
    'Chat1a1Message',
    'DiaryEntry',
    'MoodLevel',
    'Volunteer',
    'VolunteerSkill',
    'VolunteerAvailability',
    'VolunteerStatus',
    'SkillLevel',
    'DayOfWeek',
    'TriageLog',
    'RiskLevel',
    'TriageAction',
    'AdminLog',
    'AdminAction',
    'LogLevel',
    'TrainingData',
    'TrainingDataType',
    'TrainingDataStatus',
    'BaseModel'
]
