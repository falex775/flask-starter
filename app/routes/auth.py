from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
)
from email_validator import validate_email, EmailNotValidError

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _normalize_email(email: str) -> str:
    try:
        info = validate_email(email.strip(), check_deliverability=False)
        return info.normalized
    except EmailNotValidError:
        return ""


@auth_bp.post("/register")
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body required"}), 400

    name = (data.get("name") or "").strip()
    email = _normalize_email(data.get("email") or "")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request body required"}), 400

    email = _normalize_email(data.get("email") or "")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    response = jsonify({"message": "Login successful", "user": user.to_dict()})
    set_access_cookies(response, access_token)
    return response, 200


@auth_bp.post("/logout")
def logout():
    response = jsonify({"message": "Logged out successfully"})
    unset_jwt_cookies(response)
    return response


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200
