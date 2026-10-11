async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || "Request failed.");
  return data;
}

const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const todoForm = document.getElementById("todoForm");
const messageEl = document.getElementById("message");
const todoList = document.getElementById("todoList");
const titleInput = document.getElementById("title");

function setMessage(message, ok = false) {
  if (!messageEl) return;
  messageEl.textContent = message;
  messageEl.style.color = ok ? "green" : "crimson";
}

if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
      setMessage("All fields are required.");
      return;
    }

    try {
      const data = await api("/api/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      setMessage(data.message, true);
      registerForm.reset();
    } catch (error) {
      setMessage(error.message);
    }
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
      setMessage("All fields are required.");
      return;
    }

    try {
      await api("/api/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      window.location.href = "todo-test.html";
    } catch (error) {
      setMessage(error.message);
    }
  });
}

function renderTodoItem(todo) {
  const li = document.createElement("li");

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = Number(todo.is_done) === 1;

  const taskText = document.createElement("span");
  taskText.textContent = todo.title;
  taskText.style.textDecoration = checkbox.checked ? "line-through" : "none";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.textContent = "Edit";
  editButton.addEventListener("click", async () => {
    const newTitle = prompt("Edit task title:", todo.title);
    if (newTitle === null) return;
    const cleaned = newTitle.trim();
    if (!cleaned) {
      alert("Task title is required.");
      return;
    }
    try {
      await api(`/api/todos/${todo.todo_id}/title`, {
        method: "PUT",
        body: JSON.stringify({ title: cleaned }),
      });
      await loadTodos();
    } catch (error) {
      alert(error.message);
    }
  });

  checkbox.addEventListener("change", async () => {
    try {
      await api(`/api/todos/${todo.todo_id}/status`, {
        method: "PUT",
        body: JSON.stringify({ is_done: checkbox.checked ? 1 : 0 }),
      });
      taskText.style.textDecoration = checkbox.checked ? "line-through" : "none";
    } catch (error) {
      checkbox.checked = !checkbox.checked;
      alert(error.message);
    }
  });

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.textContent = "Delete";
  deleteButton.addEventListener("click", async () => {
    try {
      await api(`/api/todos/${todo.todo_id}`, { method: "DELETE" });
      await loadTodos();
    } catch (error) {
      alert(error.message);
    }
  });

  li.appendChild(checkbox);
  li.appendChild(taskText);
  li.appendChild(editButton);
  li.appendChild(deleteButton);

  return li;
}

async function loadTodos() {
  if (!todoList) return;
  try {
    const data = await api("/api/private_list");
    todoList.innerHTML = "";
    data.todos.forEach((todo) => todoList.appendChild(renderTodoItem(todo)));
  } catch (_error) {
    window.location.href = "login.html";
  }
}

if (todoForm) {
  todoForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = titleInput.value.trim();
    if (!title) {
      alert("Task title is required.");
      return;
    }
    try {
      await api("/api/todos", {
        method: "POST",
        body: JSON.stringify({ title }),
      });
      todoForm.reset();
      await loadTodos();
    } catch (error) {
      alert(error.message);
    }
  });

  loadTodos();
}

const logoutLink = document.getElementById("logoutLink");
if (logoutLink) {
  logoutLink.addEventListener("click", async (event) => {
    event.preventDefault();
    try {
      await api("/api/logout", { method: "POST" });
    } finally {
      window.location.href = "login.html";
    }
  });
}
