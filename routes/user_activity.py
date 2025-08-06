from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from extensions import db
from models.user_activity import UserActivity
from schemas.user_activity_schema import (
    CreateUserActivitySchema,
    UpdateUserActivitySchema,
    UserActivityResponseSchema,
)
from datetime import datetime
import uuid

activity_bp = Blueprint("activity", __name__)

create_schema = CreateUserActivitySchema()
update_schema = UpdateUserActivitySchema()
response_schema = UserActivityResponseSchema()


@activity_bp.route("/", methods=["POST"])
@jwt_required()
def create_activity():
    """Registrar una nueva actividad del usuario"""
    try:
        user_id = get_jwt_identity()
        # Carga solo los campos que el usuario puede enviar (sin ip_address ni user_agent)
        data = create_schema.load(request.json, partial=("ip_address", "user_agent"))

        # Obtener IP real de la petición
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        # Obtener user-agent de la petición
        user_agent = request.headers.get("User-Agent")

        activity = UserActivity(
            user_id=user_id,
            event=data["event"],
            ip_address=ip_address,
            user_agent=user_agent,
            file_id=data.get("file_id"),
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({"activity": response_schema.dump(activity)}), 201

    except ValidationError as err:
        return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


@activity_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_activities():
    """Obtener todas las actividades del usuario autenticado"""
    try:
        user_id = get_jwt_identity()
        activities = (
            UserActivity.query.filter_by(user_id=user_id)
            .order_by(UserActivity.created_at.desc())
            .all()
        )
        return jsonify({"activities": response_schema.dump(activities, many=True)}), 200

    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@activity_bp.route("/user/range", methods=["GET"])
@jwt_required()
def get_user_activities_by_date():
    """Obtener actividades del usuario autenticado en un rango de fecha"""
    try:
        user_id = get_jwt_identity()
        start = request.args.get("start")
        end = request.args.get("end")

        if not start or not end:
            return jsonify({"error": "Parámetros 'start' y 'end' requeridos"}), 400

        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)

        activities = (
            UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.created_at >= start_date,
                UserActivity.created_at <= end_date,
            )
            .order_by(UserActivity.created_at.desc())
            .all()
        )

        return jsonify({"activities": response_schema.dump(activities, many=True)}), 200

    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa ISO 8601."}), 400
    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500


@activity_bp.route("/<uuid:activity_id>", methods=["PATCH"])
@jwt_required()
def update_activity(activity_id):
    """Actualizar actividad por ID (solo del mismo usuario)"""
    try:
        user_id = get_jwt_identity()
        activity = UserActivity.query.get_or_404(activity_id)

        if str(activity.user_id) != str(user_id):
            return jsonify({"error": "Acceso denegado"}), 403

        data = update_schema.load(request.json, partial=True)

        for key, value in data.items():
            setattr(activity, key, value)

        db.session.commit()
        return jsonify({"message": "Actividad actualizada"}), 200

    except ValidationError as err:
        return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500


@activity_bp.route("/<uuid:activity_id>", methods=["DELETE"])
@jwt_required()
def delete_activity(activity_id):
    """Eliminar actividad por ID (solo del mismo usuario)"""
    try:
        user_id = get_jwt_identity()
        activity = UserActivity.query.get_or_404(activity_id)

        if str(activity.user_id) != str(user_id):
            return jsonify({"error": "Acceso denegado"}), 403

        db.session.delete(activity)
        db.session.commit()
        return jsonify({"message": "Actividad eliminada"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500
