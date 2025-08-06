from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from schemas.user_schema import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from marshmallow import ValidationError
import uuid
from marshmallow import EXCLUDE
import re

users_bp = Blueprint("users", __name__)

# Instanciar esquemas
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()
user_response_schema = UserResponseSchema()


@users_bp.route("/", methods=["GET"])
@jwt_required()
def get_users():
    """Obtener lista de usuarios (con paginación)"""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Limitar per_page a máximo 50
        per_page = min(per_page, 50)

        users = User.query.paginate(page=page, per_page=per_page, error_out=False)

        return (
            jsonify(
                {
                    "users": [user_response_schema.dump(user) for user in users.items],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": users.total,
                        "pages": users.pages,
                        "has_next": users.has_next,
                        "has_prev": users.has_prev,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_own_user():
    """Obtener el propio usuario según token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({"user": user_response_schema.dump(user)}), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    """Crear un nuevo usuario (solo admin)"""
    try:
        # Verificar si el usuario actual es admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user or current_user.privilege != "admin":
            return jsonify({"error": "Acceso denegado"}), 403

        # Validar datos de entrada
        data = user_create_schema.load(request.json)

        # Verificar si el email ya existe
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        # Verificar si el username ya existe
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "El username ya está en uso"}), 400
        
        # Verificar si el avatar_url es válido
        avatar_url = "https://api.dicebear.com/6.x/bottts-neutral/svg?seed=" + data["username"]

        # Crear nuevo usuario
        user = User(
            email=data["email"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            login_type=data.get("login_type", "email"),
            privilege=data.get("privilege", "standard"),
            avatar_url=avatar_url
        )

        # Establecer contraseña si se proporciona
        if "password" in data and data["password"]:
            user.set_password(data["password"])

        # Guardar en base de datos
        db.session.add(user)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Usuario creado exitosamente",
                    "user": user_response_schema.dump(user),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_own_user():
    """Actualizar el propio usuario según token"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Validar datos de entrada
        data = user_update_schema.load(request.json, partial=True)

        # Verificar unicidad de email si se está actualizando
        if "email" in data and data["email"] != current_user.email:
            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "El email ya está registrado"}), 400

        # Verificar unicidad de username si se está actualizando
        if "username" in data and data["username"] != current_user.username:
            if User.query.filter_by(username=data["username"]).first():
                return jsonify({"error": "El username ya está en uso"}), 400

        # Actualizar campos
        for field, value in data.items():
            setattr(current_user, field, value)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Usuario actualizado exitosamente",
                    "user": user_response_schema.dump(current_user),
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"error": "Datos inválidos", "details": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_own_user():
    """Eliminar el propio usuario según token"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # No permitir que un admin se elimine a sí mismo
        if current_user.privilege == "admin":
            return (
                jsonify(
                    {"error": "No puedes eliminar tu propia cuenta de administrador"}
                ),
                400,
            )

        db.session.delete(current_user)
        db.session.commit()

        return jsonify({"message": "Usuario eliminado exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500
