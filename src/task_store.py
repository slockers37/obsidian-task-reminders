import sqlite3
import uuid
import hashlib
from dataclasses import dataclass
from datetime import datetime

# A simple dataclass for tasks might be useful later
@dataclass
class Task:
    id: str
    file_path: str
    raw_line: str
    due: datetime | None
    status: str
    job_id: str | None

class TaskStore:
    def __init__(self, db_path: str, check_same_thread=True):
        self.conn = sqlite3.connect(db_path, check_same_thread=check_same_thread)
        self.conn.row_factory = sqlite3.Row

    def create_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                task_hash TEXT UNIQUE,
                file_path TEXT NOT NULL,
                due_datetime TEXT,
                job_id TEXT,
                status TEXT NOT NULL,
                raw_line TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_task_if_new(self, task_data: dict) -> str | None:
        """Adds a task only if it's new (based on hash). Returns new task ID or None."""
        task_id = str(uuid.uuid4())
        # Create a stable hash for the task
        task_hash = hashlib.sha256(
            (task_data['file_path'] + task_data['raw_line']).encode('utf-8')
        ).hexdigest()

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO tasks (id, task_hash, file_path, due_datetime, status, raw_line)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    task_hash,
                    task_data['file_path'],
                    task_data['due'].isoformat() if task_data.get('due') else None,
                    'scheduled',  # Default status
                    task_data['raw_line']
                )
            )
            self.conn.commit()
            return task_id
        except sqlite3.IntegrityError:
            # This happens if the UNIQUE constraint on task_hash fails
            # It means the task already exists, so we do nothing.
            return None

    def get_task(self, task_id: str) -> dict | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_tasks_by_file_path(self, file_path: str) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE file_path = ?", (file_path,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_task_job_id(self, task_id: str, job_id: str):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET job_id = ? WHERE id = ?", (job_id, task_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
