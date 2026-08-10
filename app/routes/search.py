from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.models.contact import Contact
from app.models.deal import Deal
from app.models.activity import Activity

search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/api/search"
)


# Search Endpoint
@search_bp.get("")
@jwt_required()
def search():
    uid = get_jwt_identity()
    q = request.args.get("q", "").strip()

    if not q:
        return jsonify({
            "contacts": [],
            "deals": [],
            "activities": []
        })

    contacts = Contact.query.filter(
        Contact.user_id == uid,
        or_(
            Contact.name.ilike(f"%{q}%"),
            Contact.email.ilike(f"%{q}%"),
            Contact.company.ilike(f"%{q}%"),
            Contact.phone.ilike(f"%{q}%")
        )
    ).limit(50).all()

    deals = Deal.query.filter(
        Deal.user_id == uid,
        or_(
            Deal.title.ilike(f"%{q}%"),
            Deal.notes.ilike(f"%{q}%")
        )
    ).limit(50).all()

    activities = Activity.query.filter(
        Activity.user_id == uid,
        or_(
            Activity.kind.ilike(f"%{q}%"),
            Activity.notes.ilike(f"%{q}%")
        )
    ).limit(50).all()

    return jsonify({
        "contacts": [c.to_dict() for c in contacts],
        "deals": [d.to_dict() for d in deals],
        "activities": [a.to_dict() for a in activities]
    })
