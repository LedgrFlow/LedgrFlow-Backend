from marshmallow import Schema, fields, validate, post_load
from typing import Dict, Any
import uuid
from datetime import datetime


class NotificationSchema(Schema):
    """Esquema para notificaciones"""
    
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(required=True)
    
    # Contenido de la notificación
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    
    # Estado y importancia
    is_read = fields.Bool(default=False)
    importance = fields.Str(validate=validate.OneOf(['low', 'normal', 'high', 'critical']), default='normal')
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    read_at = fields.DateTime(dump_only=True)
    
    @post_load
    def make_notification(self, data, **kwargs):
        """Crea una instancia de Notification después de la validación"""
        from models.notification import Notification, NotificationImportance
        
        # Convertir string de importancia a enum
        if 'importance' in data:
            data['importance'] = NotificationImportance(data['importance'])
        
        return Notification(**data)


class NotificationUpdateSchema(Schema):
    """Esquema para actualizar notificaciones (campos opcionales)"""
    
    title = fields.Str(validate=validate.Length(min=1, max=255), missing=None)
    content = fields.Str(validate=validate.Length(min=1), missing=None)
    is_read = fields.Bool(missing=None)
    importance = fields.Str(validate=validate.OneOf(['low', 'normal', 'high', 'critical']), missing=None)


class NotificationCreateSchema(Schema):
    """Esquema para crear notificaciones (sin user_id, se obtiene del token)"""
    
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    importance = fields.Str(validate=validate.OneOf(['low', 'normal', 'high', 'critical']), default='normal')


# Instancias de esquemas
notification_schema = NotificationSchema()
notification_list_schema = NotificationSchema(many=True)
notification_update_schema = NotificationUpdateSchema()
notification_create_schema = NotificationCreateSchema() 