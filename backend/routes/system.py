from flask import Blueprint, jsonify, session

from backend.database import get_db
from backend.repositories import find_user_by_id
from backend.security import current_user_id

system_bp = Blueprint("system", __name__)


@system_bp.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@system_bp.get("/api/session")
def session_info():
    user_id = current_user_id()
    if not user_id:
        return jsonify({"loggedIn": False}), 200
    with get_db() as conn:
        user = find_user_by_id(conn, user_id)
    if not user:
        session.clear()
        return jsonify({"loggedIn": False}), 200
    return jsonify({"loggedIn": True, "user": user})