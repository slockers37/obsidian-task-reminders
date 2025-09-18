import pytest
from task_store import TaskStore
from datetime import datetime

@pytest.fixture
def store():
    # Use in-memory SQLite database for tests
    store = TaskStore(":memory:")
    store.create_schema()
    yield store
    store.close()

def test_add_and_get_task(store):
    due_time = datetime(2025, 9, 18, 18, 30)
    task_data = {
        'file_path': '/path/to/note.md',
        'raw_line': '- [ ] Test task',
        'due': due_time
    }

    task_id = store.add_task(task_data)
    assert task_id is not None

    retrieved_task = store.get_task(task_id)
    assert retrieved_task is not None
    assert retrieved_task['id'] == task_id
    assert retrieved_task['file_path'] == '/path/to/note.md'
    assert retrieved_task['raw_line'] == '- [ ] Test task'
    assert retrieved_task['status'] == 'scheduled'
    assert retrieved_task['due_datetime'] == due_time.isoformat()

def test_get_nonexistent_task(store):
    task = store.get_task("nonexistent-id")
    assert task is None
