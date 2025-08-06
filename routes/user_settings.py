from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_settings import UserSettings
from models.user import User
from schemas.user_settings_schema import (
    user_settings_schema, 
    user_settings_list_schema, 
    user_settings_update_schema
)
from extensions import db
from sqlalchemy.exc import IntegrityError
import uuid

user_settings_bp = Blueprint('user_settings', __name__)


@user_settings_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_user_settings():
    """Obtiene las configuraciones del usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar configuraciones existentes
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            # Crear configuraciones por defecto si no existen
            settings = UserSettings(user_id=current_user_id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user_settings_schema.dump(settings)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_settings_bp.route('/settings', methods=['POST'])
@jwt_required()
def create_user_settings():
    """Crea nuevas configuraciones para el usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar si ya existen configuraciones
        existing_settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        if existing_settings:
            return jsonify({
                'success': False,
                'error': 'User settings already exist for this user'
            }), 400
        
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Agregar user_id a los datos
        data['user_id'] = current_user_id
        
        # Validar con el esquema
        settings_data = user_settings_schema.load(data)
        
        # Crear y guardar las configuraciones
        db.session.add(settings_data)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user_settings_schema.dump(settings_data),
            'message': 'User settings created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_settings_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_user_settings():
    """Actualiza las configuraciones del usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar configuraciones existentes
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            return jsonify({
                'success': False,
                'error': 'User settings not found'
            }), 404
        
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validar con el esquema de actualización
        validated_data = user_settings_update_schema.load(data)
        
        # Actualizar solo los campos proporcionados
        for field, value in validated_data.items():
            if value is not None:
                setattr(settings, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user_settings_schema.dump(settings),
            'message': 'User settings updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_settings_bp.route('/settings', methods=['DELETE'])
@jwt_required()
def delete_user_settings():
    """Elimina las configuraciones del usuario autenticado"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar configuraciones existentes
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            return jsonify({
                'success': False,
                'error': 'User settings not found'
            }), 404
        
        # Eliminar configuraciones
        db.session.delete(settings)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User settings deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_settings_bp.route('/settings/reset', methods=['POST'])
@jwt_required()
def reset_user_settings():
    """Resetea las configuraciones del usuario a los valores por defecto"""
    try:
        current_user_id = get_jwt_identity()
        
        # Buscar configuraciones existentes
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            return jsonify({
                'success': False,
                'error': 'User settings not found'
            }), 404
        
        # Resetear a valores por defecto
        settings.app_theme = 'dark'
        settings.editor_theme = 'vs-dark'
        settings.parent_accounts = {
            "Assets": "Assets",
            "Liabilities": "Liabilities", 
            "Equity": "Equity",
            "Income": "Income",
            "Expenses": "Expenses"
        }
        settings.language = 'en'
        settings.timezone = 'UTC'
        settings.time_format = '24h'
        settings.decimal_separator = '.'
        settings.thousands_separator = ','
        settings.font_size = 14
        settings.auto_format_on_save = True
        settings.auto_save_file = True
        settings.allow_account_aliases = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user_settings_schema.dump(settings),
            'message': 'User settings reset to default values'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 