from marshmallow import Schema, fields, validate
from uuid import UUID
from datetime import date, datetime


class CreateTaxRateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    short_name = fields.Str(required=False, allow_none=True)
    tax_type = fields.Str(required=False, allow_none=True)

    percentage = fields.Decimal(required=True, as_string=True)
    included_in_price = fields.Boolean(required=False, missing=False)

    applicable_to = fields.List(fields.Str(), required=False, allow_none=True)

    country = fields.Str(required=False, allow_none=True)
    region = fields.Str(required=False, allow_none=True)
    postal_code = fields.Str(required=False, allow_none=True)

    effective_from = fields.Date(required=False, allow_none=True)
    effective_to = fields.Date(required=False, allow_none=True)

class UpdateTaxRateSchema(Schema):
    name = fields.Str(required=False, allow_none=True)
    short_name = fields.Str(required=False, allow_none=True)
    tax_type = fields.Str(required=False, allow_none=True)

    percentage = fields.Decimal(required=False, allow_none=True, as_string=True)
    included_in_price = fields.Boolean(required=False, allow_none=True)

    applicable_to = fields.List(fields.Str(), required=False, allow_none=True)

    country = fields.Str(required=False, allow_none=True)
    region = fields.Str(required=False, allow_none=True)
    postal_code = fields.Str(required=False, allow_none=True)

    effective_from = fields.Date(required=False, allow_none=True)
    effective_to = fields.Date(required=False, allow_none=True)

class TaxRateResponseSchema(Schema):
    id = fields.UUID()
    name = fields.Str()
    short_name = fields.Str(allow_none=True)
    tax_type = fields.Str(allow_none=True)

    percentage = fields.Decimal(as_string=True)
    included_in_price = fields.Boolean()
    applicable_to = fields.List(fields.Str(), allow_none=True)

    country = fields.Str(allow_none=True)
    region = fields.Str(allow_none=True)
    postal_code = fields.Str(allow_none=True)

    effective_from = fields.Date(allow_none=True)
    effective_to = fields.Date(allow_none=True)

    created_at = fields.DateTime()
    updated_at = fields.DateTime()
