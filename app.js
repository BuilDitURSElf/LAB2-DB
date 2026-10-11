const path = require("path");
const express = require("express");
const session = require("express-session");
const bcrypt = require("bcryptjs");
const mysql = require("mysql2/promise");

const app = express();
const PORT = process.env.PORT || 3000;

const pool = mysql.createPool({
  host: process.env.DB_HOST || "127.0.0.1",
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER || "root",
  password: process.env.DB_PASSWORD || "",
  database: process.env.DB_NAME || "lab2_db",
  waitForConnections: true,
  connectionLimit: 10,
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: process.env.SESSION_SECRET || "change-me",
    resave: false,
    saveUninitialized: false,
    cookie: { httpOnly: true, sameSite: "lax" },
  })
);

app.use(express.static(path.join(__dirname)));

function requireAuth(req, res, next) {
  if (!req.session.user) {
    return res.status(401).json({ message: "Please log in first." });
  }
  next();
}

app.post("/api/register", async (req, res) => {
  const name = String(req.body.name || "").trim();
  const email = String(req.body.email || "").trim().toLowerCase();
  const password = String(req.body.password || "");

  if (!name || !email || !password) {
    return res.status(400).json({ message: "All fields are required." });
  }
  if (password.length < 6) {
    return res.status(400).json({ message: "Password must be at least 6 characters." });
  }

  try {
    const passwordHash = await bcrypt.hash(password, 12);

    // Sign up:
    // INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?);
    await pool.execute(
      "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
      [email, name, passwordHash]
    );

    return res.status(201).json({ message: "Registered successfully." });
  } catch (error) {
    if (error && error.code === "ER_DUP_ENTRY") {
      return res.status(409).json({ message: "Already exists." });
    }
    return res.status(500).json({ message: "Server error." });
  }
});

app.post("/api/login", async (req, res) => {
  const email = String(req.body.email || "").trim().toLowerCase();
  const password = String(req.body.password || "");

  if (!email || !password) {
    return res.status(400).json({ message: "All fields are required." });
  }

  try {
    // Log in: find the user by e-mail, then compare the password with password_hash in your code
    // SELECT user_id, name, password_hash FROM users WHERE email = ?;
    const [rows] = await pool.execute(
      "SELECT user_id, name, password_hash FROM users WHERE email = ?",
      [email]
    );

    if (!rows.length) {
      return res.status(401).json({ message: "Invalid email or password." });
    }

    const user = rows[0];
    const ok = await bcrypt.compare(password, user.password_hash);
    if (!ok) {
      return res.status(401).json({ message: "Invalid email or password." });
    }

    req.session.user = { user_id: user.user_id, name: user.name, email };
    return res.json({ message: "Logged in successfully.", user: req.session.user });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.post("/api/logout", (req, res) => {
  req.session.destroy(() => {
    res.json({ message: "Logged out successfully." });
  });
});

app.get("/api/private_list", requireAuth, async (req, res) => {
  try {
    // Show the list of the logged-in user, newest first
    // SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = ? ORDER BY todo_id DESC;
    const [rows] = await pool.execute(
      "SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = ? ORDER BY todo_id DESC",
      [req.session.user.user_id]
    );
    return res.json({ todos: rows });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.post("/api/todos", requireAuth, async (req, res) => {
  const title = String(req.body.title || "").trim();
  if (!title) {
    return res.status(400).json({ message: "Task title is required." });
  }
  try {
    // Add a to-do
    // INSERT INTO todos (user_id, title) VALUES (?, ?);
    const [result] = await pool.execute("INSERT INTO todos (user_id, title) VALUES (?, ?)", [
      req.session.user.user_id,
      title,
    ]);
    return res.status(201).json({ todo_id: result.insertId, title, is_done: 0 });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.put("/api/todos/:todoId/title", requireAuth, async (req, res) => {
  const todoId = Number(req.params.todoId);
  const title = String(req.body.title || "").trim();
  if (!todoId || !title) {
    return res.status(400).json({ message: "Invalid request." });
  }
  try {
    // Edit the title
    // UPDATE todos SET title = ? WHERE todo_id = ? AND user_id = ?;
    const [result] = await pool.execute(
      "UPDATE todos SET title = ? WHERE todo_id = ? AND user_id = ?",
      [title, todoId, req.session.user.user_id]
    );
    if (!result.affectedRows) {
      return res.status(404).json({ message: "Task not found." });
    }
    return res.json({ message: "Task updated." });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.put("/api/todos/:todoId/status", requireAuth, async (req, res) => {
  const todoId = Number(req.params.todoId);
  const isDone = Number(req.body.is_done);
  if (!todoId || ![0, 1].includes(isDone)) {
    return res.status(400).json({ message: "Invalid request." });
  }
  try {
    // Mark done (1) or not done (0)
    // UPDATE todos SET is_done = ? WHERE todo_id = ? AND user_id = ?;
    const [result] = await pool.execute(
      "UPDATE todos SET is_done = ? WHERE todo_id = ? AND user_id = ?",
      [isDone, todoId, req.session.user.user_id]
    );
    if (!result.affectedRows) {
      return res.status(404).json({ message: "Task not found." });
    }
    return res.json({ message: "Task status updated." });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.delete("/api/todos/:todoId", requireAuth, async (req, res) => {
  const todoId = Number(req.params.todoId);
  if (!todoId) {
    return res.status(400).json({ message: "Invalid request." });
  }
  try {
    // Delete
    // DELETE FROM todos WHERE todo_id = ? AND user_id = ?;
    const [result] = await pool.execute("DELETE FROM todos WHERE todo_id = ? AND user_id = ?", [
      todoId,
      req.session.user.user_id,
    ]);
    if (!result.affectedRows) {
      return res.status(404).json({ message: "Task not found." });
    }
    return res.json({ message: "Task deleted." });
  } catch (_error) {
    return res.status(500).json({ message: "Server error." });
  }
});

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "login.html"));
});

app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Server running on http://localhost:${PORT}`);
});
