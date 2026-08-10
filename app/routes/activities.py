from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.activity import Activity
from app.models.contact import Contact
from app.models.deal import Deal

activities_bp = Blueprint(
    "activities",
    __name__,
    url_prefix="/api/activities"
)


# List Activities
# Supports:
# GET /api/activities
# GET /api/activities?contact_id=2
# GET /api/activities?deal_id=4
@activities_bp.get("")
@jwt_required()
def list_activities():
    uid = int(get_jwt_identity())
    query = Activity.query.filter_by(user_id=uid)

    contact_id = request.args.get("contact_id", type=int)
    deal_id = request.args.get("deal_id", type=int)

    if contact_id is not None:
        query = query.filter_by(contact_id=contact_id)
    if deal_id is not None:
        query = query.filter_by(deal_id=deal_id)

    activities = query.order_by(Activity.happened_at.desc()).all()
    return jsonify([a.to_dict() for a in activities])


# Recent Activities Endpoint
# GET /api/activities/recent
@activities_bp.get("/recent")
@jwt_required()
def recent():
    uid = int(get_jwt_identity())
    activities = Activity.query.filter_by(user_id=uid).order_by(
        Activity.happened_at.desc()
    ).limit(10).all()

    return jsonify([a.to_dict() for a in activities])


# GET Single Activity
@activities_bp.get("/<int:id>")
@jwt_required()
def get_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()
    return jsonify(activity.to_dict())


# Create Activity
@activities_bp.post("")
@jwt_required()
def create_activity():
    uid = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get("kind"):
        return jsonify({"message": "Kind required"}), 400

    if not data.get("happened_at"):
        return jsonify({"message": "Date required"}), 400

    if data.get("contact_id"):
        if not Contact.query.filter_by(id=data["contact_id"], user_id=uid).first():
            return jsonify({"message": "Invalid contact"}), 404

    if data.get("deal_id"):
        if not Deal.query.filter_by(id=data["deal_id"], user_id=uid).first():
            return jsonify({"message": "Invalid deal"}), 404

    activity = Activity(
        user_id=uid,
        contact_id=data.get("contact_id"),
        deal_id=data.get("deal_id"),
        kind=data["kind"],
        notes=data.get("notes"),
        happened_at=datetime.fromisoformat(data["happened_at"])
    )

    db.session.add(activity)
    db.session.commit()

    return jsonify(activity.to_dict()), 201


# Update Activity
@activities_bp.put("/<int:id>")
@jwt_required()
def update_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()
    data = request.get_json()

    activity.kind = data.get("kind", activity.kind)
    activity.notes = data.get("notes", activity.notes)
    activity.contact_id = data.get("contact_id", activity.contact_id)
    activity.deal_id = data.get("deal_id", activity.deal_id)

    if data.get("happened_at"):
        activity.happened_at = datetime.fromisoformat(data["happened_at"])

    db.session.commit()
    return jsonify(activity.to_dict())


# Delete Activity
@activities_bp.delete("/<int:id>")
@jwt_required()
def delete_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()

    db.session.delete(activity)
    db.session.commit()

    return jsonify({"message": "Activity deleted"})
