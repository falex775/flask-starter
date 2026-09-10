from datetime import datetime, timezone
from app.extensions import db


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    value = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="Open", index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    activities = db.relationship(
        "Activity", backref="deal", lazy="dynamic", foreign_keys="Activity.deal_id"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "title": self.title,
            "value": self.value,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
