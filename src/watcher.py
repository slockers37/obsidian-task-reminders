import time
from watchdog.observers import Observer
import watchdog.events as events

from parser import parse_tasks
from task_store import TaskStore
from scheduler import ReminderScheduler

class MarkdownEventHandler(events.FileSystemEventHandler):
    """Handles filesystem events for markdown files."""

    def __init__(self, task_store_db_path: str, scheduler: ReminderScheduler):
        self.task_store_db_path = task_store_db_path
        self.scheduler = scheduler

    def on_any_event(self, event: events.FileSystemEvent):
        if event.is_directory:
            return
        
        if event.event_type in ('created', 'modified') and event.src_path.endswith(".md"):
            print(f"\nProcessing {event.event_type} event for: {event.src_path}")
            self._process_file(event.src_path)

    def _process_file(self, file_path: str):
        store = None
        try:
            store = TaskStore(self.task_store_db_path, check_same_thread=True)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tasks = parse_tasks(content)
            print(f"Found {len(tasks)} tasks in {file_path}.")

            for task in tasks:
                if not task['completed']:
                    task_data = {
                        'file_path': file_path,
                        'raw_line': task['raw_line'],
                        'due': task['due']
                    }
                    task_id = store.add_task_if_new(task_data)
                    if task_id and task_data['due']:
                        print(f"  - Added new task to store with ID: {task_id}")
                        try:
                            job = self.scheduler.schedule_task(task_id, task_data['due'])
                            if job:
                                store.update_task_job_id(task_id, job.id)
                                print(f"  - Scheduled job {job.id} for task {task_id}.")
                        except Exception as e:
                            print(f"  - Error scheduling task {task_id}: {e}")

        except FileNotFoundError:
            print(f"File not found during processing: {file_path}")
        except Exception as e:
            print(f"An error occurred processing file {file_path}: {e}")
        finally:
            if store:
                store.close()

class VaultWatcher:
    def __init__(self, vault_path: str, task_store_db_path: str, scheduler: ReminderScheduler):
        self.vault_path = vault_path
        self.event_handler = MarkdownEventHandler(task_store_db_path, scheduler)
        self.observer = Observer()

    def start(self):
        """Starts watching the vault path."""
        print(f"Starting watcher for vault: {self.vault_path}")
        self.observer.schedule(self.event_handler, self.vault_path, recursive=True)
        self.observer.start()
        print("Watcher started.")

    def stop(self):
        """Stops the watcher."""
        print("Stopping watcher.")
        self.observer.stop()
        self.observer.join()
        print("Watcher stopped.")