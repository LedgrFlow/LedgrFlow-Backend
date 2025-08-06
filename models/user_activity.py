import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from extensions import db


class UserActivity(db.Model):
    __tablename__ = "user_activity"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    file_id = db.Column(UUID(as_uuid=True), db.ForeignKey("files.id"), nullable=True)

    event = db.Column(db.String, nullable=False)
    ip_address = db.Column(db.String, nullable=False)
    user_agent = db.Column(db.String, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    user = db.relationship("User", backref="activities")
    file = db.relationship("File", backref="activities", lazy="joined")
