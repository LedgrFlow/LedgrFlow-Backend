# FIX: Trabajando en obtener datos de impuestos desde API externa

# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from marshmallow import ValidationError
# from extensions import db
# from models.tax_rate import TaxRate
# from schemas.tax_schema import (
#     CreateTaxRateSchema,
#     UpdateTaxRateSchema,
#     TaxRateResponseSchema,
# )
# from datetime import datetime, date, timedelta
# from sqlalchemy import or_, and_
# import requests


# TAXDATA_API_KEY = ""
# TAXDATA_ENDPOINT = "https://api.taxapi.io/v1/rates"


# tax_bp = Blueprint("tax", __name__)

# create_schema = CreateTaxRateSchema()
# update_schema = UpdateTaxRateSchema()
# response_schema = TaxRateResponseSchema()


# def fetch_tax_data_from_api(country, region=None, postal_code=None):
#     """Solicita los datos de impuestos a la API externa"""
#     params = {
#         "country": country,
#         "region": region,
#         "postal_code": postal_code,
#     }
#     headers = {"Authorization": f"Bearer {TAXDATA_API_KEY}"}
#     response = requests.get(TAXDATA_ENDPOINT, params=params, headers=headers)

#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise Exception(f"Error al obtener datos de TaxData API: {response.text}")


# @tax_bp.route("/", methods=["POST"])
# @jwt_required()
# def create_tax():
#     """Crear una nueva tasa de impuesto o retornar la más reciente si ya existe o si hay una caché válida de 48h"""
#     try:
#         data = create_schema.load(request.json)

#         country = data["country"]
#         region = data.get("region")
#         postal_code = data.get("postal_code")

#         today = date.today()
#         cutoff_date = today - timedelta(hours=48)

#         # Verificar si ya existe una tasa vigente o registrada hace menos de 48h
#         cached = (
#             TaxRate.query.filter_by(
#                 country=country,
#                 region=region,
#                 postal_code=postal_code,
#             )
#             .filter(TaxRate.effective_from >= cutoff_date)
#             .order_by(TaxRate.effective_from.desc())
#             .first()
#         )

#         if cached:
#             return (
#                 jsonify(
#                     {
#                         "message": "Ya existe un impuesto registrado recientemente (menos de 48h).",
#                         "tax_rate": response_schema.dump(cached),
#                     }
#                 ),
#                 200,
#             )

#         # Si no existe o expiró la caché, consultar a la API externa
#         tax_data = fetch_tax_data_from_api(country, region, postal_code)

#         new_tax = TaxRate(
#             name=tax_data.get("name", "Desconocido"),
#             short_name=tax_data.get("short_name"),
#             tax_type=tax_data.get("type"),
#             percentage=tax_data["rate"],
#             included_in_price=tax_data.get("included_in_price", False),
#             applicable_to=tax_data.get("applicable_to"),
#             country=country,
#             region=region,
#             postal_code=postal_code,
#             effective_from=today,
#             effective_to=None,
#         )

#         db.session.add(new_tax)
#         db.session.commit()

#         return (
#             jsonify(
#                 {
#                     "message": "Tasa de impuesto registrada desde API externa",
#                     "tax_rate": response_schema.dump(new_tax),
#                 }
#             ),
#             201,
#         )

#     except ValidationError as err:
#         return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
#     except Exception as e:
#         print(e)
#         db.session.rollback()
#         return jsonify({"error": "Error interno del servidor"}), 500


# @tax_bp.route("/search", methods=["GET"])
# @jwt_required()
# def search_tax_rates():
#     """Buscar impuestos por país, región/código postal y fecha o rango"""
#     try:
#         country = request.args.get("country")
#         region = request.args.get("region")
#         postal_code = request.args.get("postal_code")
#         date_from = request.args.get("start")
#         date_to = request.args.get("end")

#         query = TaxRate.query

#         if not country:
#             return jsonify({"error": "El parámetro 'country' es requerido"}), 400

#         query = query.filter(TaxRate.country == country)

#         if region:
#             query = query.filter(TaxRate.region == region)
#         elif postal_code:
#             query = query.filter(TaxRate.postal_code == postal_code)

#         if date_from and date_to:
#             start_date = datetime.fromisoformat(date_from).date()
#             end_date = datetime.fromisoformat(date_to).date()
#             query = query.filter(
#                 or_(
#                     and_(
#                         TaxRate.effective_from <= end_date,
#                         TaxRate.effective_to >= start_date,
#                     ),
#                     and_(
#                         TaxRate.effective_from <= end_date, TaxRate.effective_to == None
#                     ),
#                 )
#             )
#         else:
#             # Si no hay fechas, buscar las tasas más recientes por vigencia
#             today = date.today()
#             query = query.filter(
#                 or_(
#                     and_(TaxRate.effective_from <= today, TaxRate.effective_to == None),
#                     and_(
#                         TaxRate.effective_from <= today, TaxRate.effective_to >= today
#                     ),
#                 )
#             )

#         results = query.order_by(TaxRate.effective_from.desc()).all()
#         return jsonify({"tax_rates": response_schema.dump(results, many=True)}), 200

#     except ValueError:
#         return jsonify({"error": "Formato de fecha inválido. Usa ISO 8601."}), 400
#     except Exception as e:
#         print(e)
#         return jsonify({"error": "Error interno del servidor"}), 500


# @tax_bp.route("/<uuid:tax_id>", methods=["PATCH"])
# @jwt_required()
# def update_tax(tax_id):
#     """Actualizar una tasa de impuesto (solo admins)"""
#     try:
#         # Aquí podrías validar si el usuario es admin con un decorador personalizado
#         tax = TaxRate.query.get_or_404(tax_id)
#         data = update_schema.load(request.json, partial=True)

#         for key, value in data.items():
#             setattr(tax, key, value)

#         db.session.commit()
#         return jsonify({"message": "Tasa actualizada correctamente"}), 200

#     except ValidationError as err:
#         return jsonify({"error": "Datos inválidos", "details": err.messages}), 400
#     except Exception:
#         db.session.rollback()
#         return jsonify({"error": "Error interno del servidor"}), 500
