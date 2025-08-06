from marshmallow import Schema, fields, validate, ValidationError
from models.file import File

class FileCreateSchema(Schema):
    """Esquema para crear archivo"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    file_content = fields.Str(required=True, validate=validate.Length(min=1))
    file_extension = fields.Str(validate=validate.OneOf(['.ledger', '.md', '.txt', '.markdown']))

class FileUpdateSchema(Schema):
    """Esquema para actualizar archivo"""
    name = fields.Str(validate=validate.Length(min=1, max=255))
    file_content = fields.Str(validate=validate.Length(min=1))

class FileResponseSchema(Schema):
    """Esquema para respuesta de archivo (sin contenido)"""
    id = fields.Str()
    name = fields.Str()
    file_extension = fields.Str()
    file_size = fields.Int()
    user_id = fields.Str()
    uploaded_at = fields.DateTime()
    modified_at = fields.DateTime()

class FileResponseWithContentSchema(Schema):
    """Esquema para respuesta de archivo (con contenido)"""
    id = fields.Str()
    name = fields.Str()
    file_extension = fields.Str()
    file_size = fields.Int()
    file_content = fields.Str()
    user_id = fields.Str()
    uploaded_at = fields.DateTime()
    modified_at = fields.DateTime()

def validate_file_extension(filename):
    """Validador personalizado para extensión de archivo"""
    if not File.is_allowed_extension(filename):
        raise ValidationError('Tipo de archivo no permitido. Solo se permiten: .ledger, .md, .txt, .markdown') 