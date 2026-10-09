def find_user_by_id(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id AS id, name, email FROM users WHERE user_id = %s", (user_id,))
        return cursor.fetchone()


def find_user_for_login(conn, email):
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (email,))
        return cursor.fetchone()


def create_user(conn, email, name, password_hash):
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
            (email, name, password_hash),
        )
        return cursor.lastrowid


def list_user_todos(conn, user_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT todo_id AS id, title, is_done, created_at
            FROM todos WHERE user_id = %s ORDER BY todo_id DESC""",
            (user_id,),
        )
        return cursor.fetchall()


def find_user_todo(conn, todo_id, user_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT todo_id AS id, title, is_done, created_at
            FROM todos WHERE todo_id = %s AND user_id = %s""",
            (todo_id, user_id),
        )
        return cursor.fetchone()


def create_todo(conn, user_id, title):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (user_id, title))
        return cursor.lastrowid


def update_todo(conn, todo_id, user_id, fields, values):
    with conn.cursor() as cursor:
        cursor.execute(
            f"UPDATE todos SET {', '.join(fields)} WHERE todo_id = %s AND user_id = %s",
            [*values, todo_id, user_id],
        )
        return cursor.rowcount


def delete_todo(conn, todo_id, user_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, user_id))
        return cursor.rowcount