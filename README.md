# LAB2-DB

Login and private to-do list app using Node.js, Express, and MySQL (no SQLite).

## Setup

1. Create a MySQL database, for example: `lab2_db`.
2. Run `/home/runner/work/LAB2-DB/LAB2-DB/schema.sql` in your database.
3. Install dependencies:

```bash
npm install
```

4. Set environment variables if needed:

- `DB_HOST` (default `127.0.0.1`)
- `DB_PORT` (default `3306`)
- `DB_USER` (default `root`)
- `DB_PASSWORD` (default empty)
- `DB_NAME` (default `lab2_db`)
- `SESSION_SECRET` (recommended to set)
- `PORT` (default `3000`)

5. Run:

```bash
npm start
```

6. Open `http://localhost:3000`.

## Implemented SQL operations

- Sign up  
  `INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?);`
- Log in  
  `SELECT user_id, name, password_hash FROM users WHERE email = ?;`
- Private list  
  `SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = ? ORDER BY todo_id DESC;`
- Add todo  
  `INSERT INTO todos (user_id, title) VALUES (?, ?);`
- Edit title  
  `UPDATE todos SET title = ? WHERE todo_id = ? AND user_id = ?;`
- Mark done/undone  
  `UPDATE todos SET is_done = ? WHERE todo_id = ? AND user_id = ?;`
- Delete  
  `DELETE FROM todos WHERE todo_id = ? AND user_id = ?;`
