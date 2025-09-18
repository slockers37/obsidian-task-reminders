import time
import os
from pathlib import Path
from watcher import VaultWatcher

def test_watcher_detects_new_file(tmp_path):
    """An integration test to verify the watcher detects file creation."""
    # tmp_path is a pytest fixture that provides a temporary directory
    vault_dir = tmp_path
    test_file_path = vault_dir / "test_file.md"

    print(f"Using temporary vault for test: {vault_dir}")

    # 1. Initialize and start the watcher
    watcher = VaultWatcher(vault_path=str(vault_dir))
    watcher.start()

    try:
        # 2. Create a dummy markdown file
        print(f"Creating test file: {test_file_path}")
        Path(test_file_path).touch()

        # 3. Wait for the event to be processed
        time.sleep(1) # Allow time for the filesystem event to propagate

        # 4. Check if the watcher detected the file
        processed = watcher.event_handler.processed_events
        print(f"Watcher detected events: {processed}")
        assert any(Path(p).samefile(test_file_path) for p in processed)
        print("Success: Watcher correctly detected the new file.")

    finally:
        # 5. Stop the watcher
        watcher.stop()
