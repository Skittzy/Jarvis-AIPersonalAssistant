"""Functions for storing tasks in .json file."""
import json
import os

FILE_NAME = "data/todos.json"

def load_tasks():
    if not os.path.exists(FILE_NAME):
        return []  # file doesn’t exist, return empty list
    
    with open(FILE_NAME, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []  # file is empty or corrupted, return empty list
        
def load_tasks_as_string():
    # Converts tasks.json into a string to give to Gemini
    
    tasks = load_tasks()
    if not tasks:
        return "No tasks currently."

    task_lines = []
    for task in tasks:
        if "task" in task and task["task"].strip():
            name = task["task"].strip()
            completed = task.get("done", False)
            task_lines.append(f'Task: "{name}" - Completed: {completed}')
    
    if not task_lines:
        return "No tasks currently."

    return "\n".join(task_lines)


def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(task_text):
    tasks = load_tasks()
    tasks.append({"task": task_text, "done": False})
    save_tasks(tasks)

def mark_done(task_name):
    tasks = load_tasks()
    for task in tasks:
        if task["task"].lower() == task_name.lower():
            task["done"] = True
            save_tasks(tasks)

def reset_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            f.write("[]")

