from marshmallow import Schema, fields, validate

class CurrencyRateSchema(Schema):
    """Schema for currency rate response"""
    success = fields.Boolean(required=True)
    base_currency = fields.String(required=True)
    rates = fields.Dict(keys=fields.String(), values=fields.Float(), required=True)
    timestamp = fields.String(required=True)
    source = fields.String(required=True)

class CurrencyConversionSchema(Schema):
    """Schema for currency conversion response"""
    success = fields.Boolean(required=True)
    amount = fields.Float(required=True)
    from_currency = fields.String(required=True)
    to_currency = fields.String(required=True)
    converted_amount = fields.Float(required=True)
    rate = fields.Float(required=True)
    timestamp = fields.String(required=True)
    source = fields.String(required=True)

class NewsItemSchema(Schema):
    """Schema for individual news item"""
    title = fields.String(required=True)
    description = fields.String(required=True)
    url = fields.String(required=True)
    published_date = fields.String(required=True)
    provider = fields.String(required=True)
    category = fields.String(required=True)
    image_url = fields.String(required=True)

class NewsResponseSchema(Schema):
    """Schema for news response"""
    success = fields.Boolean(required=True)
    category = fields.String(required=True)
    count = fields.Integer(required=True)
    news = fields.List(fields.Nested(NewsItemSchema), required=True)
    timestamp = fields.String(required=True)
    source = fields.String(required=True)

class ServiceStatusSchema(Schema):
    """Schema for service status response"""
    currency_service = fields.Dict(required=True)
    news_service = fields.Dict(required=True)
    timestamp = fields.String(required=True)

class ErrorResponseSchema(Schema):
    """Schema for error responses"""
    success = fields.Boolean(required=True)
    error = fields.String(required=True)
    timestamp = fields.String(required=True) 