import os

from flask import Blueprint, request, jsonify #, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.contact import Contact
from app.models.activity import Activity

#from app.config.Config import WEBSITE_LEAD_USER_ID #gives import error
WEBSITE_LEAD_USER_ID = int(os.environ.get("WEBSITE_LEAD_USER_ID", "1"))

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

@contacts_bp.get("/<int:id>/timeline")
@jwt_required()
def contact_timeline(id):
    user_id = int(get_jwt_identity())
    Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    activities = (
        Activity.query.filter_by(user_id=user_id, contact_id=id)
        .order_by(Activity.happened_at.desc(), Activity.id.desc())
        .all()
    )
    return jsonify([activity.to_dict() for activity in activities])

@contacts_bp.get("/<int:id>")
@jwt_required()
def get_contact(id):
    user_id = int(get_jwt_identity())
    contact = Contact.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(contact.to_dict())


def _create_contact(data, user_id):
    name = (data.get("name") or "").strip()

    if not name:
        raise ValueError("Name is required")

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

    return contact

@contacts_bp.post("")
@jwt_required()
def create_contact():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    try:
        contact = _create_contact(data, user_id)
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    return jsonify(contact.to_dict()), 201


@contacts_bp.post("/public") # See TODO below
def create_public_contact():
    data = request.get_json() or {}

    try:
        contact = _create_contact(
            data,
            WEBSITE_LEAD_USER_ID
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({
        "message": "Thanks "+contact.name+"! We'll be in touch soon."
    }), 201


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



"""
#TODO: Because this endpoint is public, anyone can potentially call it directly. add validation and some basic anti-spam protection.
Also consider adding:

 - **Rate limiting** — prevents someone from submitting thousands of contacts.
- **Honeypot field or CAPTCHA** — reduces bot submissions.
- **Email validation** — basic format checking.
- **CSRF protection** if your authentication/session architecture requires it.
- **Duplicate detection** if you don't want repeated submissions.
- **Logging** of suspicious submissions, without logging sensitive information unnecessarily.

@contacts_bp.post("/public")
def create_public_contact():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    company = (data.get("company") or "").strip()
    notes = (data.get("notes") or "").strip()

    # Validation
    if not name:
        return jsonify({"message": "Name is required"}), 400

    if not email:
        return jsonify({"message": "Email is required"}), 400

    if len(name) > 200:
        return jsonify({"message": "Name is too long"}), 400

    if len(email) > 320:
        return jsonify({"message": "Email is too long"}), 400

    if len(phone) > 50:
        return jsonify({"message": "Phone number is too long"}), 400

    if len(company) > 200:
        return jsonify({"message": "Company name is too long"}), 400

    if len(notes) > 5000:
        return jsonify({"message": "Message is too long"}), 400

    contact = Contact(
        #user_id=1,  # Website lead owner
        user_id=WEBSITE_LEAD_USER_ID,
        name=name,
        email=email or None,
        phone=phone or None,
        company=company or None,
        notes=notes or None,
    )

    try:
        db.session.add(contact)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to create public contact")

        return jsonify({
            "message": "Unable to submit your request."
        }), 500

    return jsonify({
        "message": "Thanks! We'll be in touch soon."
    }), 201
"""