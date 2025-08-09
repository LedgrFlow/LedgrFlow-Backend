from marshmallow import Schema, fields, validate, post_load


class UserSettingsSchema(Schema):
    """Esquema para configuraciones de usuario"""

    # id = fields.UUID(load_only==True)
    # user_id = fields.UUID(load_only==True)

    # Theme settings
    app_theme = fields.Str(
        validate=validate.OneOf(["dark", "light", "system"]), default="light"
    )
    app_glass_mode = fields.Bool(default=False)
    editor_theme = fields.Str(default="vs-dark")

    # Account structure configuration
    parent_accounts = fields.Dict(
        keys=fields.Str(),
        values=fields.Str(),
        default={
            "Assets": "Assets",
            "Liabilities": "Liabilities",
            "Equity": "Equity",
            "Income": "Income",
            "Expenses": "Expenses",
        },
    )

    # Language and localization
    language = fields.Str(validate=validate.OneOf(["en", "es"]), default="es")
    timezone = fields.Str(default="UTC")
    time_format = fields.Str(validate=validate.OneOf(["12h", "24h"]), default="24h")
    decimal_separator = fields.Str(validate=validate.OneOf([".", ","]), default=".")
    thousands_separator = fields.Str(
        validate=validate.OneOf([",", ".", " "]), default=","
    )

    # Editor settings
    font_size = fields.Int(validate=validate.Range(min=8, max=72), default=14)
    auto_format_on_save = fields.Bool(default=True)
    auto_save_file = fields.Bool(default=True)
    editor_word_wrap = fields.Bool(default=True)
    editor_minimap_enabled = fields.Bool(default=True)
    editor_line_numbers = fields.Bool(default=True)

    # Account settings
    allow_account_aliases = fields.Bool(default=True)

    @post_load
    def make_user_settings(self, data, **kwargs):
        from models.user_settings import UserSettings

        return UserSettings(**data)


class UserSettingsUpdateSchema(Schema):
    """Esquema para actualizar configuraciones de usuario (campos opcionales)"""

    app_theme = fields.Str(
        validate=validate.OneOf(["dark", "light", "system"]), missing=None
    )
    app_glass_mode = fields.Bool(missing=None)
    editor_theme = fields.Str(missing=None)
    parent_accounts = fields.Dict(keys=fields.Str(), values=fields.Str(), missing=None)
    language = fields.Str(validate=validate.OneOf(["en", "es"]), missing=None)
    timezone = fields.Str(missing=None)
    time_format = fields.Str(validate=validate.OneOf(["12h", "24h"]), missing=None)
    decimal_separator = fields.Str(validate=validate.OneOf([".", ","]), missing=None)
    thousands_separator = fields.Str(
        validate=validate.OneOf([",", ".", " "]), missing=None
    )

    # Nuevos campos de editor
    font_size = fields.Int(validate=validate.Range(min=8, max=72), missing=None)
    auto_format_on_save = fields.Bool(missing=None)
    auto_save_file = fields.Bool(missing=None)
    editor_word_wrap = fields.Bool(missing=None)
    editor_minimap_enabled = fields.Bool(missing=None)
    editor_line_numbers = fields.Bool(missing=None)

    allow_account_aliases = fields.Bool(missing=None)


# Instancias de esquemas
user_settings_schema = UserSettingsSchema()
user_settings_list_schema = UserSettingsSchema(many=True)
user_settings_update_schema = UserSettingsUpdateSchema()
