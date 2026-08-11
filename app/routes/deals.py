from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models.deal import Deal
from app.models.contact import Contact

deals_bp = Blueprint(
    "deals",
    __name__,
    url_prefix="/api/deals"
)


# GET Deals
# Supports:
# GET /api/deals
# GET /api/deals?status=Open
# GET /api/deals?contact_id=2
# GET /api/deals?page=1&per_page=20
@deals_bp.get("")
@jwt_required()
def list_deals():
    uid = get_jwt_identity()
    query = Deal.query.filter_by(user_id=uid)

    status = request.args.get("status")
    contact_id = request.args.get("contact_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if status:
        query = query.filter_by(status=status)
    if contact_id is not None:
        query = query.filter_by(contact_id=contact_id)

    pagination = query.order_by(Deal.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "items": [d.to_dict() for d in pagination.items],
        "page": page,
        "pages": pagination.pages,
        "total": pagination.total
    })


# GET Single Deal
@deals_bp.get("/<int:id>")
@jwt_required()
def get_deal(id):
    uid = get_jwt_identity()
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()
    return jsonify(deal.to_dict())


# Create Deal
@deals_bp.post("")
@jwt_required()
def create_deal():
    uid = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"message": "Title required"}), 400

    contact_id = data.get("contact_id")
    if contact_id:
        contact = Contact.query.filter_by(id=contact_id, user_id=uid).first()
        if not contact:
            return jsonify({"message": "Invalid contact"}), 404

    deal = Deal(
        user_id=uid,
        contact_id=contact_id,
        title=data["title"],
        value=data.get("value", 0),
        status=data.get("status", "Open"),
        notes=data.get("notes")
    )

    db.session.add(deal)
    db.session.commit()

    return jsonify(deal.to_dict()), 201


# Update Deal
@deals_bp.put("/<int:id>")
@jwt_required()
def update_deal(id):
    uid = get_jwt_identity()
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()
    data = request.get_json()

    deal.title = data.get("title", deal.title)
    deal.value = data.get("value", deal.value)
    deal.status = data.get("status", deal.status)
    deal.notes = data.get("notes", deal.notes)
    deal.contact_id = data.get("contact_id", deal.contact_id)

    db.session.commit()
    return jsonify(deal.to_dict())


# Delete Deal
@deals_bp.delete("/<int:id>")
@jwt_required()
def delete_deal(id):
    uid = get_jwt_identity()
    deal = Deal.query.filter_by(id=id, user_id=uid).first_or_404()

    db.session.delete(deal)
    db.session.commit()

    return jsonify({"message": "Deal deleted"})


# Dashboard Summary Endpoint
# GET /api/deals/summary
@deals_bp.get("/summary")
@jwt_required()
def summary():
    uid = get_jwt_identity()

    total_value = db.session.query(func.sum(Deal.value)).filter_by(
        user_id=uid, status="Open"
    ).scalar() or 0

    won = Deal.query.filter_by(user_id=uid, status="Won").count()
    lost = Deal.query.filter_by(user_id=uid, status="Lost").count()
    open_count = Deal.query.filter_by(user_id=uid, status="Open").count()

    return jsonify({
        "pipeline_value": total_value,
        "open": open_count,
        "won": won,
        "lost": lost
    })
