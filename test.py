import requests
from flask import Blueprint, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict()), 200


BASE = "http://localhost:5000/api/auth"


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f"  ({detail})" if detail and not ok else ""))
    return ok


def main():
    s = requests.Session()  # session keeps cookies automatically

    ok_all = True

    # /me without auth
    r = requests.get(f"{BASE}/me")
    ok_all &= check("/me returns 401 when unauthenticated", r.status_code == 401, f"got {r.status_code}")

    print("\n" + ("ALL TESTS PASSED" if ok_all else "SOME TESTS FAILED"))


if __name__ == "__main__":
    main()
