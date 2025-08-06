import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from extensions import db

class File(db.Model):
    """Modelo de Archivo"""
    __tablename__ = 'files'
    
    # Tipos de archivo permitidos
    ALLOWED_EXTENSIONS = {'.ledger', '.md', '.txt', '.markdown'}
    
    # Campos principales
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    file_extension = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Tamaño en bytes
    file_content = db.Column(db.Text, nullable=False)  # Contenido del archivo
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relación con usuario
    user = db.relationship('User', backref=db.backref('files', lazy=True, cascade='all, delete-orphan'))
    
    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()
    
    @staticmethod
    def is_allowed_extension(filename):
        """Verifica si la extensión del archivo está permitida"""
        if '.' not in filename:
            return False
        extension = '.' + filename.rsplit('.', 1)[1].lower()
        return extension in File.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_extension(filename):
        """Obtiene la extensión del archivo"""
        if '.' not in filename:
            return ''
        return '.' + filename.rsplit('.', 1)[1].lower()
    
    def update_content(self, new_content):
        """Actualiza el contenido del archivo y recalcula el tamaño"""
        self.file_content = new_content
        self.file_size = len(new_content.encode('utf-8'))
        self.modified_at = datetime.utcnow()
    
    def to_dict(self):
        """Convierte el archivo a diccionario"""
        return {
            'id': str(self.id),
            'name': self.name,
            'file_extension': self.file_extension,
            'file_size': self.file_size,
            'user_id': str(self.user_id),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None
        }
    
    def to_dict_with_content(self):
        """Convierte el archivo a diccionario incluyendo el contenido"""
        data = self.to_dict()
        data['file_content'] = self.file_content
        return data
    
    def __repr__(self):
        return f'<File {self.name}>' 