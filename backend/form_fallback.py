from markupsafe import escape
from flask import render_template_string, request


def is_browser_form():
    return request.mimetype == "application/x-www-form-urlencoded"


def auth_error_page(kind, message, values):
    register = kind == "register"
    title = "Create your account" if register else "Welcome back"
    action = "/api/register" if register else "/api/login"
    fields = """
        <label>Full Name</label><input name="name" value="{name}">
        <label>Email</label><input name="email" value="{email}">
    """ if register else """
        <label>Email</label><input name="email" value="{email}">
    """
    password_fields = """
        <label>Password</label><input type="password" name="password">
        <label>Confirm Password</label><input type="password" name="confirm_password">
    """ if register else """
        <label>Password</label><input type="password" name="password">
    """
    next_page = "login.html" if register else "register.html"
    return render_template_string(
        """
        <!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ title }}</title><link rel="stylesheet" href="/css/style.css"></head>
        <body class="auth-page"><main class="auth-card"><div class="eyebrow">Personal workspace</div>
        <h1>{{ title }}</h1><p class="form-message">{{ message }}</p>
        <form action="{{ action }}" method="post">{{ fields|safe }}{{ password_fields|safe }}
        <button class="primary-button" type="submit">Continue</button></form>
        <p class="register-link"><a href="/{{ next_page }}">Back</a></p></main></body></html>
        """,
        title=title,
        message=escape(message),
        action=action,
        fields=fields.format(name=escape(values.get("name", "")), email=escape(values.get("email", ""))),
        password_fields=password_fields,
        next_page=next_page,
    )


def todo_error_page(message, title="Add a task"):
    return render_template_string(
        """
        <!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{ title }}</title><link rel="stylesheet" href="/css/style.css"></head>
        <body class="todo-page"><main class="todo-shell"><div class="eyebrow">Personal workspace</div>
        <h1>{{ title }}</h1><p class="form-message">{{ message }}</p>
        <form action="/api/todos" method="post"><label>Task title</label>
        <input name="title" maxlength="200"><button class="primary-button" type="submit">Add task</button></form>
        <p class="register-link"><a href="/todo-test.html">Back to tasks</a></p></main></body></html>
        """,
        title=title,
        message=escape(message),
    )