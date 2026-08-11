from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from email_validator import validate_email, EmailNotValidError

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "email", "password")):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        validate_email(data["email"])
    except EmailNotValidError:
        return jsonify({"success": False, "message": "Invalid email address"}), 400

    if len(data["password"]) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400

    user = User(
        name=data["name"],
        email=data["email"]
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)

    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)

    return jsonify({
        "access_token": token,
        "user": user.to_dict()
    })


@auth_bp.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    return jsonify(user.to_dict())
