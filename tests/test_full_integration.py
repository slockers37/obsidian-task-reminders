import pytest
import time
from pathlib import Path
from datetime import datetime

from watcher import VaultWatcher
from task_store import TaskStore

@pytest.fixture
def store():
    s = TaskStore(":memory:", check_same_thread=False)
    s.create_schema()
    yield s
    s.close()

def test_watcher_parser_store_integration(store, tmp_path):
    vault_dir = tmp_path
    test_note_path = vault_dir / "test_note.md"
    task_line = "- [ ] A test task for integration ⏰ 10:00 📅 2025-12-25"

    # 1. Start watcher
    watcher = VaultWatcher(vault_path=str(vault_dir), task_store=store)
    watcher.start()

    try:
        # 2. Create a file with a task
        print(f"\nCreating test file: {test_note_path}")
        test_note_path.write_text(task_line)
        time.sleep(1)  # Give watcher time to process

        # 3. Verify task was added to store
        print(f"Checking store for tasks from: {test_note_path}")
        tasks_in_store = store.get_tasks_by_file_path(str(test_note_path))
        print(f"Found tasks in store: {tasks_in_store}")
        
        assert len(tasks_in_store) == 1
        task = tasks_in_store[0]
        assert task['raw_line'] == task_line
        assert task['status'] == 'scheduled'
        assert task['due_datetime'] == datetime(2025, 12, 25, 10, 0).isoformat()
        print("\nSuccess: Integration test passed. Task was correctly added to the store.")

    finally:
        watcher.stop()
