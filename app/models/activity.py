from datetime import datetime
from app.extensions import db


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    contact_id = db.Column(
        db.Integer,
        db.ForeignKey("contacts.id"),
        nullable=True
    )

    deal_id = db.Column(
        db.Integer,
        db.ForeignKey("deals.id"),
        nullable=True
    )

    kind = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

    happened_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="activities")
    contact = db.relationship("Contact", back_populates="activities")
    deal = db.relationship("Deal", back_populates="activities")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "deal_id": self.deal_id,
            "kind": self.kind,
            "notes": self.notes,
            "happened_at": self.happened_at.isoformat() if self.happened_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
