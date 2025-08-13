"""
Modelo base para todos os modelos da aplicação
"""

from datetime import datetime
from app import db
from sqlalchemy import DateTime
from sqlalchemy.sql import func


class BaseModel(db.Model):
    """
    Modelo base com campos comuns para todas as tabelas
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = db.Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    def save(self):
        """Salva o objeto no banco de dados"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Remove o objeto do banco de dados"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
