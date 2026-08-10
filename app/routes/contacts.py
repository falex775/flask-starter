from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.contact import Contact

contacts_bp = Blueprint(
    "contacts",
    __name__,
    url_prefix="/api/contacts"
)


# GET Contacts
# Supports:
# GET /api/contacts
# GET /api/contacts?q=john
# GET /api/contacts?page=1&per_page=20
@contacts_bp.get("")
@jwt_required()
def list_contacts():
    user_id = get_jwt_identity()

    q = request.args.get("q")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = Contact.query.filter_by(user_id=user_id)

    if q:
        query = query.filter(
            or_(
                Contact.name.ilike(f"%{q}%"),
                Contact.email.ilike(f"%{q}%"),
                Contact.company.ilike(f"%{q}%"),
                Contact.phone.ilike(f"%{q}%")
            )
        )

    pagination = query.order_by(Contact.name).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "items": [c.to_dict() for c in pagination.items],
        "page": page,
        "pages": pagination.pages,
        "total": pagination.total
    })


# GET Single Contact
@contacts_bp.get("/<int:id>")
@jwt_required()
def get_contact(id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(contact.to_dict())


# Create Contact
@contacts_bp.post("")
@jwt_required()
def create_contact():
    data = request.get_json()
    user_id = get_jwt_identity()

    if not data or not data.get("name"):
        return jsonify({"message": "Name required"}), 400

    contact = Contact(
        user_id=user_id,
        name=data["name"],
        email=data.get("email"),
        phone=data.get("phone"),
        company=data.get("company"),
        notes=data.get("notes")
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify(contact.to_dict()), 201


# Update Contact
@contacts_bp.put("/<int:id>")
@jwt_required()
def update_contact(id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    data = request.get_json()

    contact.name = data.get("name", contact.name)
    contact.email = data.get("email", contact.email)
    contact.phone = data.get("phone", contact.phone)
    contact.company = data.get("company", contact.company)
    contact.notes = data.get("notes", contact.notes)

    db.session.commit()
    return jsonify(contact.to_dict())


# Delete Contact
@contacts_bp.delete("/<int:id>")
@jwt_required()
def delete_contact(id):
    user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()

    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message": "Deleted"})
