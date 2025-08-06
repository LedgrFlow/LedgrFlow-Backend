from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from extensions import db
import enum


class NotificationImportance(enum.Enum):
    """Enum para los niveles de importancia de las notificaciones"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Contenido de la notificación
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Estado y importancia
    is_read = Column(Boolean, default=False, nullable=False)
    importance = Column(Enum(NotificationImportance), default=NotificationImportance.NORMAL, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)  # Null por defecto ya que no se ha leído
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title}>'
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def mark_as_unread(self):
        """Marca la notificación como no leída"""
        self.is_read = False
        self.read_at = None 