from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import Notification, NotificationImportance
from models.user import User
from schemas.notification_schema import (
    notification_schema, 
    notification_list_schema, 
    notification_update_schema,
    notification_create_schema
)
from extensions import db
from sqlalchemy.exc import IntegrityError
import uuid

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    """Obtiene todas las notificaciones del usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parámetros de consulta opcionales
        is_read = request.args.get('is_read', type=str)
        importance = request.args.get('importance', type=str)
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        
        # Construir query base
        query = Notification.query.filter_by(user_id=current_user_id)
        
        # Aplicar filtros si se proporcionan
        if is_read is not None:
            if is_read.lower() == 'true':
                query = query.filter_by(is_read=True)
            elif is_read.lower() == 'false':
                query = query.filter_by(is_read=False)
        
        if importance:
            try:
                importance_enum = NotificationImportance(importance.lower())
                query = query.filter_by(importance=importance_enum)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid importance level'
                }), 400
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(Notification.created_at.desc())
        
        # Aplicar paginación
        total_count = query.count()
        notifications = query.limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'data': notification_list_schema.dump(notifications),
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/<uuid:notification_id>', methods=['GET'])
@jwt_required()
def get_notification_by_id(notification_id):
    """Obtiene una notificación específica por ID"""
    try:
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    """Crea una nueva notificación para el usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validar con el esquema de creación
        validated_data = notification_create_schema.load(data)
        
        # Agregar user_id
        validated_data['user_id'] = current_user_id
        
        # Crear la notificación
        notification = Notification(**validated_data)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification),
            'message': 'Notification created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/system', methods=['POST'])
def create_system_notification():
    """Crea una notificación del sistema para un usuario específico (sin autenticación)"""
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Verificar que se proporcione user_id
        if 'user_id' not in data:
            return jsonify({
                'success': False,
                'error': 'user_id is required for system notifications'
            }), 400
        
        # Validar con el esquema completo
        validated_data = notification_schema.load(data)
        
        # Crear la notificación
        notification = Notification(**validated_data)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification),
            'message': 'System notification created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/<uuid:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    """Actualiza una notificación específica"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar la notificación
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validar con el esquema de actualización
        validated_data = notification_update_schema.load(data)
        
        # Actualizar solo los campos proporcionados
        for field, value in validated_data.items():
            if value is not None:
                if field == 'importance':
                    setattr(notification, field, NotificationImportance(value))
                else:
                    setattr(notification, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification),
            'message': 'Notification updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/<uuid:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Elimina una notificación específica"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar la notificación
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Eliminar la notificación
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/<uuid:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """Marca una notificación como leída"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar la notificación
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Marcar como leída
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification),
            'message': 'Notification marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/<uuid:notification_id>/unread', methods=['POST'])
@jwt_required()
def mark_notification_as_unread(notification_id):
    """Marca una notificación como no leída"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar la notificación
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Marcar como no leída
        notification.mark_as_unread()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': notification_schema.dump(notification),
            'message': 'Notification marked as unread'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_notifications_as_read():
    """Marca todas las notificaciones del usuario como leídas"""
    try:
        current_user_id = get_jwt_identity()
        
        # Obtener todas las notificaciones no leídas
        unread_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).all()
        
        # Marcar todas como leídas
        for notification in unread_notifications:
            notification.mark_as_read()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(unread_notifications)} notifications marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notifications_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Obtiene el número de notificaciones no leídas"""
    try:
        current_user_id = get_jwt_identity()
        
        unread_count = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': unread_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 