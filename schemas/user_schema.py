from marshmallow import Schema, fields, validate, ValidationError
import re

from marshmallow import Schema, fields, validate, ValidationError
import re
from marshmallow import EXCLUDE


class UserCreateSchema(Schema):
    """Esquema para crear usuario"""

    email = fields.Email(required=True, validate=validate.Length(max=255))
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(
                r"^@.+$",
                error="El nombre de usuario debe comenzar con '@'",
            ),
        ],
    )
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    password = fields.Str(validate=validate.Length(min=6, max=100))
    login_type = fields.Str(
        validate=validate.OneOf(["email", "google", "facebook", "twitter"])
    )
    avatar_url = fields.Str(allow_none=True)
    description = fields.Str(
        validate=validate.Length(max=1000), allow_none=True, missing=""
    )


class UserUpdateSchema(Schema):
    """Esquema para actualizar usuario"""

    class Meta:
        unknown = EXCLUDE  # Ignora cualquier campo no declarado

    # email = fields.Email(validate=validate.Length(max=255))
    email = fields.Email(dump_only=True)  # Solo lectura
    # username = fields.Str(
    #     validate=[
    #         validate.Length(min=3, max=50),
    #         validate.Regexp(
    #             r"^[a-zA-Z0-9_]+$",
    #             error="Username solo puede contener letras, números y guiones bajos",
    #         ),
    #     ]
    # )
    first_name = fields.Str(validate=validate.Length(max=100))
    last_name = fields.Str(validate=validate.Length(max=100))
    privilege = fields.Str(validate=validate.OneOf(["standard", "admin", "moderator"]))
    avatar_url = fields.Str(allow_none=True)
    description = fields.Str(validate=validate.Length(max=1000), allow_none=True)


class UserLoginSchema(Schema):
    """Esquema para login"""

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


class UserResponseSchema(Schema):
    """Esquema para respuesta de usuario"""

    # id = fields.Str()
    email = fields.Email()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    privilege = fields.Str()
    login_type = fields.Str()
    email_verified = fields.Bool()
    avatar_url = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
