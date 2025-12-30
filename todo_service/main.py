from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import string, random

app = FastAPI(title="To-Do Service")

# ===== Модель для POST запроса =====
class Task(BaseModel):
    title: str
    description: str = ""
    completed: bool = False

# ===== Подключение к SQLite =====
conn = sqlite3.connect("tasks.db", check_same_thread=False)
cur = conn.cursor()

# ===== Создаем таблицу, если её нет =====
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT False
)
""")
conn.commit()

# ===== POST /tasks =====
@app.post("/tasks")
def create_task(task: Task):
    cur.execute(
        "INSERT INTO tasks (task_id, title, description, completed) VALUES (NULL, ?, ?, False)",
        (task.title, task.description, )
    )
    conn.commit()
    return {"task": task}

# ===== GET /tasks =====
@app.get("/tasks")
def fetch_all_tasks():
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    if rows is None:
        raise HTTPException(status_code=404, detail="No tasks")
    return [
        {"id": row[0],
        "title": row[1],
        "description": row[2],
        "completed": row[3]}
        for row in rows
    ]

# ===== GET /tasks/{id} =====
@app.get("/tasks/{id}")
def fetch_one_task(task_id: int):
    cur.execute("SELECT * FROM tasks WHERE task_id = ?", (int(task_id), ))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No such task")
    
    task_id, title, description, completed = row
    return {
        "id": task_id,
        "title": title,
        "description": description,
        "completed": completed}

@app.put("/tasks/{id}")
def update_task(task_id: int, updated_task: Task):
    cur.execute("SELECT * FROM tasks WHERE task_id = ?", (int(task_id), ))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No such task")
    
    title = updated_task.title
    description = updated_task.description
    completed = updated_task.completed

    cur.execute("UPDATE tasks SET title = ?, description = ?, completed = ? WHERE task_id = ?", 
                (title, description, completed, int(task_id), ))
    conn.commit()
    return updated_task

@app.delete("/tasks/{id}")
def delete_task(task_id: int):
    cur.execute("SELECT * FROM tasks WHERE task_id = ?", (int(task_id), ))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No such task")

    cur.execute("DELETE FROM tasks WHERE task_id = ?", (task_id, ))
    conn.commit()
    return f"task {task_id} is deleted"
