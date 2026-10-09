# Lab 2: Login and To-Do Application

## Team

- Member 1: **[name and university ID]** - **[contribution]**
- Member 2: **[name and university ID]** - **[contribution, or remove this line if working alone]**

Replace the placeholders before submitting.

## Technology

- Backend: Python, Flask, Flask-Session, PyMySQL, bcrypt
- Frontend: HTML, CSS, and browser JavaScript
- Database: MySQL, database `registration`

The backend uses plain parameterized SQL. No ORM is used.

## Run From An Empty Machine

1. Install Python 3.11 or newer and MySQL.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install Python dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Build the database. Run `schema.sql` with a MySQL account allowed to create databases:

   ```bash
   mysql -u root -p < schema.sql
   ```

5. Create the local environment file and edit the MySQL values:

   ```bash
   cp .env.example .env
   ```

6. Start the server:

   ```bash
   python app.py
   ```

7. Open http://127.0.0.1:5000.

The frontend is kept in `frontend/`; Flask serves it at the root URL while the backend remains in `backend/`.

Never commit `.env`; it is ignored by `.gitignore`. Commit only `.env.example` with fake values.

## Features

- R1: Registration with name, email, password, confirmation, duplicate-email handling, and automatic login.
- R2: Login, shared invalid-credentials message, and logout.
- R3: Session-protected personal todo list ordered newest first.
- R4-R7: Add, edit, complete/uncomplete, and delete todos with ownership checks.
- R8: Browser and server validation with the exact assignment messages.
- R9: bcrypt password hashes, parameterized SQL, and the user ID taken from the session.
- R10: Consistent responsive interface, empty state, loading feedback, error feedback, and visible completed tasks.

## Database And Security Answers

**(a) Why do update and delete include `AND user_id = ?`?**

The todo ID comes from the browser and can be changed by a user. The session provides the trusted logged-in user ID. Including both values means a request can modify or delete a row only when that row belongs to the logged-in user. Removing the condition would allow one user to modify another user's todo by guessing its ID.

**(b) What happens for a missing `user_id`?**

MySQL rejects the insert because the foreign-key value does not reference an existing user. This is referential integrity, which is a foreign-key constraint.

**(c) Why store a hash instead of the password?**

The original password should never be recoverable from the database. bcrypt stores a salted, deliberately slow one-way hash; login verifies the typed password against that hash without storing the password itself.

**(d) Why validate an empty name when the column is `NOT NULL`?**

`NOT NULL` rejects SQL `NULL`, not an empty string or whitespace. Application validation trims the input and rejects empty text before the insert.

## Screenshots To Add Before Submission

Add at least these four screenshots under `screenshots/` and link them here:

1. Registration page showing validation messages.
2. Login page.
3. Todo list containing an open and a completed todo.
4. The site at approximately 360px wide.