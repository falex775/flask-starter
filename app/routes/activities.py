from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.activity import Activity
from app.models.contact import Contact
from app.models.deal import Deal

activities_bp = Blueprint("activities", __name__, url_prefix="/api/activities")


def _parse_iso(value: str):
    # Handles trailing Z from JavaScript .toISOString()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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


@activities_bp.get("/recent")
@jwt_required()
def recent():
    uid = int(get_jwt_identity())
    activities = (
        Activity.query.filter_by(user_id=uid)
        .order_by(Activity.happened_at.desc())
        .limit(10)
        .all()
    )
    return jsonify([a.to_dict() for a in activities])


@activities_bp.get("/<int:id>")
@jwt_required()
def get_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()
    return jsonify(activity.to_dict())


@activities_bp.post("")
@jwt_required()
def create_activity():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    kind = (data.get("kind") or "").strip()
    happened_at = data.get("happened_at")
    if not kind:
        return jsonify({"message": "Kind is required"}), 400
    if not happened_at:
        return jsonify({"message": "Date is required"}), 400

    contact_id = data.get("contact_id")
    if contact_id:
        if not Contact.query.filter_by(id=contact_id, user_id=uid).first():
            return jsonify({"message": "Invalid contact"}), 404

    deal_id = data.get("deal_id")
    if deal_id:
        if not Deal.query.filter_by(id=deal_id, user_id=uid).first():
            return jsonify({"message": "Invalid deal"}), 404

    try:
        dt = _parse_iso(happened_at)
    except ValueError:
        return jsonify({"message": "Invalid date format"}), 400

    activity = Activity(
        user_id=uid,
        contact_id=contact_id or None,
        deal_id=deal_id or None,
        kind=kind,
        notes=(data.get("notes") or "").strip() or None,
        happened_at=dt,
    )

    db.session.add(activity)
    db.session.commit()
    return jsonify(activity.to_dict()), 201


@activities_bp.put("/<int:id>")
@jwt_required()
def update_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()
    data = request.get_json() or {}

    activity.kind = (data.get("kind") or activity.kind).strip()
    activity.notes = (data.get("notes", activity.notes) or "").strip() or None

    new_contact_id = data.get("contact_id")
    if new_contact_id is not None:
        if new_contact_id == 0:
            activity.contact_id = None
        elif not Contact.query.filter_by(id=new_contact_id, user_id=uid).first():
            return jsonify({"message": "Invalid contact"}), 404
        else:
            activity.contact_id = new_contact_id

    new_deal_id = data.get("deal_id")
    if new_deal_id is not None:
        if new_deal_id == 0:
            activity.deal_id = None
        elif not Deal.query.filter_by(id=new_deal_id, user_id=uid).first():
            return jsonify({"message": "Invalid deal"}), 404
        else:
            activity.deal_id = new_deal_id

    if data.get("happened_at"):
        try:
            activity.happened_at = _parse_iso(data["happened_at"])
        except ValueError:
            return jsonify({"message": "Invalid date format"}), 400

    db.session.commit()
    return jsonify(activity.to_dict())


@activities_bp.delete("/<int:id>")
@jwt_required()
def delete_activity(id):
    uid = int(get_jwt_identity())
    activity = Activity.query.filter_by(id=id, user_id=uid).first_or_404()

    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Activity deleted"})
