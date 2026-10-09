
const todoForm = document.getElementById("todoForm");
const titleInput = document.getElementById("title");
const todoList = document.getElementById("todoList");

todoForm.addEventListener("submit", function(event) {
    event.preventDefault();

    const taskTitle = titleInput.value.trim();

    if (taskTitle === "") {
        return;
    }

    const li = document.createElement("li");

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";

    const taskText = document.createElement("span");
    taskText.textContent = taskTitle;

    checkbox.addEventListener("change", function() {
        if (checkbox.checked) {
            taskText.style.textDecoration = "line-through";
        } else {
            taskText.style.textDecoration = "none";
        }
    });

    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Delete";
    deleteButton.type = "button";

    deleteButton.addEventListener("click", function() {
        li.remove();
    });

    li.appendChild(checkbox);
    li.appendChild(taskText);
    li.appendChild(deleteButton);

    todoList.appendChild(li);

    titleInput.value = "";
});
