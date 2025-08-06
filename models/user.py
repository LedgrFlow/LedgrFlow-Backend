import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from extensions import db
import bcrypt

class User(db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    # Tipos de login
    LOGIN_EMAIL = 'email'
    LOGIN_GOOGLE = 'google'
    LOGIN_FACEBOOK = 'facebook'
    LOGIN_TWITTER = 'twitter'
    
    # Tipos de privilegios
    PRIVILEGE_STANDARD = 'standard'
    PRIVILEGE_ADMIN = 'admin'
    PRIVILEGE_MODERATOR = 'moderator'
    
    # Campos principales
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Opcional para login social
    privilege = db.Column(db.String(20), default=PRIVILEGE_STANDARD, nullable=False)
    login_type = db.Column(db.String(20), default=LOGIN_EMAIL, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.String(1000), default='', nullable=True)  # Nueva propiedad opcional

    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()
    
    def set_password(self, password):
        """Encripta y guarda la contraseña"""
        if password:
            salt = bcrypt.gensalt()
            self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin password)"""
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'description': self.description,
            'privilege': self.privilege,
            'login_type': self.login_type,
            'email_verified': self.email_verified,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>' 