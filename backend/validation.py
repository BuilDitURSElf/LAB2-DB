def registration_errors(name, email, password, confirm_password):
    errors = {}
    if not name:
        errors["name"] = "Name is required"
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"
    if not confirm_password:
        errors["confirm_password"] = "Confirm password is required"
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match"
    return errors


def login_errors(email, password):
    errors = {}
    if not email:
        errors["email"] = "Email is required"
    if not password:
        errors["password"] = "Password is required"
    return errors


def todo_title_error(title):
    if not title:
        return "Title is required"
    if len(title) > 200:
        return "Title is too long"
    return None