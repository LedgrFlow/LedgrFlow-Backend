from marshmallow import Schema, fields, validate, ValidationError
from uuid import UUID
from datetime import datetime


class CreateUserActivitySchema(Schema):
    # user_id = fields.UUID(required=True)
    event = fields.Str(required=True, validate=validate.Length(min=1))
    # ip_address = fields.Str(required=True, validate=validate.Length(min=7))
    # user_agent = fields.Str(required=False, allow_none=True)
    file_id = fields.UUID(required=False, allow_none=True)


class UpdateUserActivitySchema(Schema):
    event = fields.Str(required=False, allow_none=True)
    ip_address = fields.Str(required=False, allow_none=True)
    user_agent = fields.Str(required=False, allow_none=True)
    file_id = fields.UUID(required=False, allow_none=True)


class UserActivityResponseSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    event = fields.Str()
    ip_address = fields.Str()
    user_agent = fields.Str(allow_none=True)
    file_id = fields.UUID(allow_none=True)
    created_at = fields.DateTime()
