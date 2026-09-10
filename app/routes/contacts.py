from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.contact import Contact

contacts_bp = Blueprint("contacts", __name__, url_prefix="/api/contacts")


@contacts_bp.get("")
@jwt_required()
def list_contacts():
    user_id = int(get_jwt_identity())
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = Contact.query.filter_by(user_id=user_id)

    if q:
        query = query.filter(
            or_(
                Contact.name.ilike(f"%{q}%"),
                Contact.email.ilike(f"%{q}%"),
                Contact.company.ilike(f"%{q}%"),
                Contact.phone.ilike(f"%{q}%"),
            )
        )

    pagination = query.order_by(Contact.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "items": [c.to_dict() for c in pagination.items],
            "page": page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    )


@contacts_bp.get("/<int:id>")
@jwt_required()
def get_contact(id):
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(contact.to_dict())


@contacts_bp.post("")
@jwt_required()
def create_contact():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"message": "Name is required"}), 400

    contact = Contact(
        user_id=user_id,
        name=name,
        email=(data.get("email") or "").strip() or None,
        phone=(data.get("phone") or "").strip() or None,
        company=(data.get("company") or "").strip() or None,
        notes=(data.get("notes") or "").strip() or None,
    )

    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201


@contacts_bp.put("/<int:id>")
@jwt_required()
def update_contact(id):
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json() or {}

    contact.name = (data.get("name") or contact.name).strip()
    contact.email = (data.get("email", contact.email) or "").strip() or None
    contact.phone = (data.get("phone", contact.phone) or "").strip() or None
    contact.company = (data.get("company", contact.company) or "").strip() or None
    contact.notes = (data.get("notes", contact.notes) or "").strip() or None

    db.session.commit()
    return jsonify(contact.to_dict())


@contacts_bp.delete("/<int:id>")
@jwt_required()
def delete_contact(id):
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()

    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contact deleted"})
