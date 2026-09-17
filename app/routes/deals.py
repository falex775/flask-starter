from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models.deal import Deal
from app.models.contact import Contact
from app.models.activity import Activity

deals_bp = Blueprint("deals", __name__, url_prefix="/api/deals")


@deals_bp.get("")
@jwt_required()
def list_deals():
    uid = int(get_jwt_identity())
    query = Deal.query.filter_by(user_id=uid)

    status = request.args.get("status", "").strip()
    contact_id = request.args.get("contact_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    if status:
        query = query.filter_by(status=status)
    if contact_id is not None:
        query = query.filter_by(contact_id=contact_id)

    pagination = query.order_by(Deal.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "items": [d.to_dict() for d in pagination.items],
            "page": page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    )


@deals_bp.get("/<int:id>/timeline")
@jwt_required()
def deal_timeline(id):
    uid = int(get_jwt_identity())
    Deal.query.filter_by(id=id, user_id=uid).first_or_404()
    activities = (
        Activity.query.filter_by(user_id=uid, deal_id=id)
        .order_by(Activity.happened_at.desc(), Activity.id.desc())
        .all()
    )
    return jsonify([activity.to_dict() for activity in activities])


@deals_bp.get("/<int:id>")
@jwt_required()
def get_deal(id):
    uid = int(get_jwt_identity())
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()
    return jsonify(deal.to_dict())


@deals_bp.post("")
@jwt_required()
def create_deal():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"message": "Title is required"}), 400

    contact_id = data.get("contact_id")
    if contact_id:
        contact = Contact.query.filter_by(id=contact_id, user_id=uid).first()
        if not contact:
            return jsonify({"message": "Invalid contact"}), 404

    deal = Deal(
        user_id=uid,
        contact_id=contact_id,
        title=title,
        value=float(data.get("value", 0) or 0),
        status=(data.get("status") or "Open").strip(),
        notes=(data.get("notes") or "").strip() or None,
    )

    db.session.add(deal)
    db.session.commit()
    return jsonify(deal.to_dict()), 201


@deals_bp.put("/<int:id>")
@jwt_required()
def update_deal(id):
    uid = int(get_jwt_identity())
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()
    data = request.get_json() or {}

    deal.title = (data.get("title") or deal.title).strip()
    deal.value = float(data.get("value", deal.value) or 0)
    deal.status = (data.get("status") or deal.status).strip()
    deal.notes = (data.get("notes", deal.notes) or "").strip() or None

    new_contact_id = data.get("contact_id")
    if new_contact_id is not None:
        if new_contact_id == 0:
            deal.contact_id = None
        else:
            contact = Contact.query.filter_by(id=new_contact_id, user_id=uid).first()
            if not contact:
                return jsonify({"message": "Invalid contact"}), 404
            deal.contact_id = new_contact_id

    db.session.commit()
    return jsonify(deal.to_dict())


@deals_bp.delete("/<int:id>")
@jwt_required()
def delete_deal(id):
    uid = int(get_jwt_identity())
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()

    db.session.delete(deal)
    db.session.commit()
    return jsonify({"message": "Deal deleted"})


@deals_bp.get("/summary")
@jwt_required()
def summary():
    uid = int(get_jwt_identity())

    pipeline_value = (
        db.session.query(func.sum(Deal.value)).filter_by(
            user_id=uid, status="Open"
        ).scalar()
        or 0
    )

    return jsonify(
        {
            "pipeline_value": float(pipeline_value),
            "open": Deal.query.filter_by(user_id=uid, status="Open").count(),
            "won": Deal.query.filter_by(user_id=uid, status="Won").count(),
            "lost": Deal.query.filter_by(user_id=uid, status="Lost").count(),
        }
    )
