import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "lab2.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

app = Flask(__name__, static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SESSION_SECRET", "dev-secret-change-me")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()


def current_user_id():
    return session.get("user_id")


def require_auth():
    user_id = current_user_id()
    if not user_id:
        return None, jsonify({"error": "Authentication required"}), 401
    return user_id, None, None


@app.get("/")
def home():
    return redirect("/login.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/session")
def session_info():
    user_id = current_user_id()
    if not user_id:
        return jsonify({"loggedIn": False}), 200

    with get_db() as conn:
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not user:
        session.clear()
        return jsonify({"loggedIn": False}), 200

    return jsonify(
        {
            "loggedIn": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
        }
    )


@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    password_hash = generate_password_hash(password)

    try:
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name, email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email is already registered"}), 409

    session.clear()
    session["user_id"] = user_id
    return jsonify({"message": "Registered successfully"}), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    with get_db() as conn:
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"message": "Login successful"}), 200


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.get("/api/todos")
def list_todos():
    user_id, error_response, status = require_auth()
    if error_response:
        return error_response, status

    with get_db() as conn:
        todos = conn.execute(
            """
            SELECT id, title, is_done, created_at, updated_at
            FROM todos
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()

    return jsonify(
        [
            {
                "id": todo["id"],
                "title": todo["title"],
                "is_done": bool(todo["is_done"]),
                "created_at": todo["created_at"],
                "updated_at": todo["updated_at"],
            }
            for todo in todos
        ]
    )


@app.post("/api/todos")
def create_todo():
    user_id, error_response, status = require_auth()
    if error_response:
        return error_response, status

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO todos (user_id, title, is_done) VALUES (?, ?, 0)",
            (user_id, title),
        )
        conn.commit()
        todo_id = cursor.lastrowid

        todo = conn.execute(
            """
            SELECT id, title, is_done, created_at, updated_at
            FROM todos
            WHERE id = ? AND user_id = ?
            """,
            (todo_id, user_id),
        ).fetchone()

    return (
        jsonify(
            {
                "id": todo["id"],
                "title": todo["title"],
                "is_done": bool(todo["is_done"]),
                "created_at": todo["created_at"],
                "updated_at": todo["updated_at"],
            }
        ),
        201,
    )


@app.put("/api/todos/<int:todo_id>")
def update_todo(todo_id):
    user_id, error_response, status = require_auth()
    if error_response:
        return error_response, status

    data = request.get_json(silent=True) or {}
    title = data.get("title")
    is_done = data.get("is_done")

    if title is None and is_done is None:
        return jsonify({"error": "Nothing to update"}), 400

    fields = []
    values = []

    if title is not None:
        cleaned_title = str(title).strip()
        if not cleaned_title:
            return jsonify({"error": "title cannot be empty"}), 400
        fields.append("title = ?")
        values.append(cleaned_title)

    if is_done is not None:
        if not isinstance(is_done, bool):
            return jsonify({"error": "is_done must be true or false"}), 400
        fields.append("is_done = ?")
        values.append(1 if is_done else 0)

    values.extend([todo_id, user_id])

    with get_db() as conn:
        cursor = conn.execute(
            f"""
            UPDATE todos
            SET {", ".join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
            """,
            values,
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Todo not found"}), 404
        conn.commit()

        todo = conn.execute(
            """
            SELECT id, title, is_done, created_at, updated_at
            FROM todos
            WHERE id = ? AND user_id = ?
            """,
            (todo_id, user_id),
        ).fetchone()

    return jsonify(
        {
            "id": todo["id"],
            "title": todo["title"],
            "is_done": bool(todo["is_done"]),
            "created_at": todo["created_at"],
            "updated_at": todo["updated_at"],
        }
    )


@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id):
    user_id, error_response, status = require_auth()
    if error_response:
        return error_response, status

    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM todos WHERE id = ? AND user_id = ?",
            (todo_id, user_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Todo not found"}), 404
        conn.commit()

    return jsonify({"message": "Todo deleted"}), 200


init_db()

if __name__ == "__main__":
    app.run(debug=True)
