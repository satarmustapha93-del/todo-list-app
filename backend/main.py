from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB = Path("/tmp/todo.db")

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

@asynccontextmanager
async def lifespan(app):
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL DEFAULT 0,
            reminder TEXT, timer_end TEXT, created_at TEXT NOT NULL)""")
    yield

app = FastAPI(title="Little List", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class NewTask(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    reminder: str | None = None

class Changes(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    done: bool | None = None
    reminder: str | None = None
    timer_end: str | None = None
    position: int | None = None

def as_task(row):
    return {**dict(row), "done": bool(row["done"])}

@app.get("/api/tasks")
def tasks():
    with connect() as db:
        return [as_task(row) for row in db.execute("SELECT * FROM tasks ORDER BY position, id")]

@app.post("/api/tasks", status_code=201)
def add_task(task: NewTask):
    title = task.title.strip()
    if not title:
        raise HTTPException(400, "A task needs a title")
    with connect() as db:
        position = db.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM tasks").fetchone()[0]
        cur = db.execute("INSERT INTO tasks(title, position, reminder, created_at) VALUES(?,?,?,?)", (title, position, task.reminder, datetime.now(timezone.utc).isoformat()))
        return as_task(db.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone())

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, changes: Changes):
    fields = changes.model_dump(exclude_unset=True)
    if "title" in fields:
        fields["title"] = fields["title"].strip()
        if not fields["title"]:
            raise HTTPException(400, "A task needs a title")
    if "done" in fields:
        fields["done"] = int(fields["done"])
    if not fields:
        raise HTTPException(400, "No changes supplied")
    with connect() as db:
        if not db.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone():
            raise HTTPException(404, "Task not found")
        db.execute("UPDATE tasks SET " + ", ".join(f"{key}=?" for key in fields) + " WHERE id=?", (*fields.values(), task_id))
        return as_task(db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with connect() as db:
        cur = db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if not cur.rowcount:
            raise HTTPException(404, "Task not found")
