# TODO: BD para almacenar tasas de impuestos

# import uuid
# from datetime import datetime
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from extensions import db


# class TaxRate(db.Model):
#     __tablename__ = "tax_rates"

#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

#     # Identificación y descripción del impuesto
#     name = db.Column(db.String, nullable=False)  # Ej: "Impuesto al Valor Agregado"
#     short_name = db.Column(db.String, nullable=True)  # Ej: "IVA", "RET_ISR"
#     tax_type = db.Column(
#         db.String, nullable=True
#     )  # Ej: "VAT", "Sales", "Excise", "Withholding"

#     # Valor y aplicación
#     percentage = db.Column(db.Numeric(6, 4), nullable=False)  # Ej: 0.1600 = 16%
#     included_in_price = db.Column(db.Boolean, default=False)
#     applicable_to = db.Column(
#         JSONB, nullable=True
#     )  # Lista: ["goods", "services"], etc.

#     # Ubicación geográfica
#     country = db.Column(db.String, nullable=True)  # ISO: "MX", "US"
#     region = db.Column(db.String, nullable=True)  # Ej: "CDMX", "Baja California"
#     postal_code = db.Column(
#         db.String, nullable=True
#     )  # Opcional: puede ser único o rango

#     # Fechas de vigencia
#     effective_from = db.Column(db.Date, nullable=True)
#     effective_to = db.Column(db.Date, nullable=True)

#     # Control de auditoría
#     created_at = db.Column(
#         db.DateTime(timezone=True), default=datetime.utcnow, nullable=False
#     )
#     updated_at = db.Column(
#         db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
#     )

#     def __repr__(self):
#         return f"<TaxRate {self.short_name or self.name} {self.percentage * 100:.2f}%>"
