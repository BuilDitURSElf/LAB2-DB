from flask import Blueprint, jsonify, request

from backend.database import get_db
from backend.form_fallback import is_browser_form, todo_error_page
from backend.repositories import create_todo, delete_todo, find_user_todo, list_user_todos, update_todo
from backend.security import login_required
from backend.validation import todo_title_error

todos_bp = Blueprint("todos", __name__)


def todo_response(todo):
    return {"id": todo["id"], "title": todo["title"], "is_done": bool(todo["is_done"]), "created_at": todo["created_at"]}


@todos_bp.get("/api/todos")
@login_required
def list_todos(user_id):
    with get_db() as conn:
        todos = list_user_todos(conn, user_id)
    return jsonify([todo_response(todo) for todo in todos])


@todos_bp.post("/api/todos")
@login_required
def add_todo(user_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    title = (data.get("title") or "").strip()
    error = todo_title_error(title)
    if error:
        if is_browser_form():
            return todo_error_page(error), 400
        return jsonify({"error": error}), 400
    with get_db() as conn:
        todo_id = create_todo(conn, user_id, title)
        conn.commit()
        todo = find_user_todo(conn, todo_id, user_id)
    if is_browser_form():
        from flask import redirect

        return redirect("/todo-test.html")
    return jsonify(todo_response(todo)), 201


@todos_bp.put("/api/todos/<int:todo_id>")
@login_required
def edit_todo(user_id, todo_id):
    data = request.get_json(silent=True) or request.form.to_dict()
    title = data.get("title")
    is_done = data.get("is_done")
    if title is None and is_done is None:
        return jsonify({"error": "Nothing to update"}), 400
    fields, values = [], []
    if title is not None:
        cleaned_title = str(title).strip()
        error = todo_title_error(cleaned_title)
        if error:
            return jsonify({"error": error}), 400
        fields.append("title = %s")
        values.append(cleaned_title)
    if is_done is not None:
        if not isinstance(is_done, bool):
            return jsonify({"error": "is_done must be true or false"}), 400
        fields.append("is_done = %s")
        values.append(1 if is_done else 0)
    with get_db() as conn:
        if update_todo(conn, todo_id, user_id, fields, values) == 0:
            return jsonify({"error": "Todo not found"}), 404
        conn.commit()
        todo = find_user_todo(conn, todo_id, user_id)
    return jsonify(todo_response(todo))


@todos_bp.delete("/api/todos/<int:todo_id>")
@login_required
def remove_todo(user_id, todo_id):
    with get_db() as conn:
        if delete_todo(conn, todo_id, user_id) == 0:
            return jsonify({"error": "Todo not found"}), 404
        conn.commit()
    return jsonify({"message": "Todo deleted"}), 200