from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from extensions import db
from models.user import User
from schemas.user_schema import UserCreateSchema, UserLoginSchema, UserResponseSchema
from marshmallow import ValidationError
import traceback

auth_bp = Blueprint('auth', __name__)

# Instanciar esquemas
user_create_schema = UserCreateSchema()
user_login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    try:
        # Validar datos de entrada
        data = user_create_schema.load(request.json)
        
        # Verificar si el email ya existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Verificar si el username ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El username ya está en uso'}), 400
        
        vatar_url = "https://api.dicebear.com/6.x/bottts-neutral/svg?seed=" + data["username"]

        
        # Crear nuevo usuario
        user = User(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            login_type=data.get('login_type', 'email'),
            avatar_url=data.get('avatar_url', vatar_url)
        )
        
        # Establecer contraseña si se proporciona
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Guardar en base de datos
        db.session.add(user)
        db.session.commit()
        
        # Generar token JWT
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user_response_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = user_login_schema.load(request.json)
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        if not user.check_password(data['password']):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return jsonify({
            'message': 'Login exitoso',
            'user': user_response_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    except ValidationError as e:
        return jsonify({'error': 'Datos inválidos', 'details': e.messages}), 400
    except Exception as e:
        traceback.print_exc()  # <-- Esto imprime el stacktrace completo
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    """Validar si el token de acceso actual es válido"""
    try:
        # Si llegamos aquí, el token es válido
        # El decorador @jwt_required() ya se encarga de validar el token
        return jsonify({
            'message': 'Token válido',
            'valid': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500
    

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        return jsonify({
            'access_token': new_access_token
        }), 200
    except Exception as e:
        return jsonify({'error': 'No se pudo refrescar el token'}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener información del usuario actual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'user': user_response_schema.dump(user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500 