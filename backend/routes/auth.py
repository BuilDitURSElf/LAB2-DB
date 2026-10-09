import pymysql
from flask import Blueprint, jsonify, request, session

from backend.database import get_db
from backend.form_fallback import auth_error_page, is_browser_form
from backend.repositories import create_user, find_user_for_login
from backend.security import hash_password, verify_password
from backend.validation import login_errors, registration_errors

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/register")
def register():
    data = request.get_json(silent=True) or request.form.to_dict()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    errors = registration_errors(name, email, password, confirm_password)
    if errors:
        if is_browser_form():
            return auth_error_page("register", next(iter(errors.values())), data), 400
        return jsonify({"error": next(iter(errors.values())), "errors": errors}), 400
    try:
        with get_db() as conn:
            user_id = create_user(conn, email, name, hash_password(password))
            conn.commit()
    except pymysql.err.IntegrityError as error:
        if error.args and error.args[0] == 1062:
            if is_browser_form():
                return auth_error_page("register", "Email Already Exists", data), 409
            return jsonify({"error": "Email Already Exists"}), 409
        raise
    session.clear()
    session["user_id"] = user_id
    if is_browser_form():
        from flask import redirect

        return redirect("/todo-test.html")
    return jsonify({"message": "Registered successfully"}), 201


@auth_bp.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    errors = login_errors(email, password)
    if errors:
        if is_browser_form():
            return auth_error_page("login", next(iter(errors.values())), data), 400
        return jsonify({"error": next(iter(errors.values())), "errors": errors}), 400
    with get_db() as conn:
        user = find_user_for_login(conn, email)
    if not user or not verify_password(password, user["password_hash"]):
        if is_browser_form():
            return auth_error_page("login", "Invalid email or password", data), 401
        return jsonify({"error": "Invalid email or password"}), 401
    session.clear()
    session["user_id"] = user["user_id"]
    if is_browser_form():
        from flask import redirect

        return redirect("/todo-test.html")
    return jsonify({"message": "Login successful"}), 200


@auth_bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200