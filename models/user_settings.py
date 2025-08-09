from sqlalchemy import Column, String, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from extensions import db


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )

    # Theme settings
    app_theme = Column(String(20), default="dark")  # dark, light, system
    app_glass_mode = Column(Boolean, default=False)  # true, false
    editor_theme = Column(String(50), default="vs-dark")  # vscode themes

    # Account structure configuration
    parent_accounts = Column(
        JSON,
        default={
            "Assets": "Assets",
            "Liabilities": "Liabilities",
            "Equity": "Equity",
            "Income": "Income",
            "Expenses": "Expenses",
        },
    )

    # Language and localization
    language = Column(String(10), default="es")  # en, es
    timezone = Column(String(50), default="UTC")
    time_format = Column(String(20), default="24h")  # 12h, 24h
    decimal_separator = Column(String(5), default=".")  # . or ,
    thousands_separator = Column(String(5), default=",")  # , or .

    # Editor settings
    font_size = Column(Integer, default=14)
    auto_format_on_save = Column(Boolean, default=True)
    auto_save_file = Column(Boolean, default=True)
    editor_word_wrap = Column(Boolean, default=True)
    editor_minimap_enabled = Column(Boolean, default=True)
    editor_line_numbers = Column(Boolean, default=True)

    # Account settings
    allow_account_aliases = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings {self.user_id}>"
