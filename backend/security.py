from functools import wraps

import bcrypt
from flask import jsonify, session


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def current_user_id():
    return session.get("user_id")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = current_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        return view(user_id, *args, **kwargs)

    return wrapped