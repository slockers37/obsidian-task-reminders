import requests
from dotenv import load_dotenv

from config import AppConfig, load_config
from task_store import TaskStore

class _GotifySenderInternal:
    """Internal sender class to keep logic organized."""
    def __init__(self, config: AppConfig, store: TaskStore):
        self.config = config
        self.store = store

    def send(self, task_id: str):
        print(f"--- Preparing to send reminder for task: {task_id} ---")
        task = self.store.get_task(task_id)

        if not task:
            print(f"Error: Could not find task with ID {task_id} in the store.")
            return

        try:
            url = f"{self.config.gotify.url}/message"
            headers = {"X-Gotify-Key": self.config.gotify.token}
            task_text = task['raw_line'].split(']', 1)[-1].strip()

            payload = {
                "title": "Obsidian Task Reminder",
                "message": task_text,
                "priority": 5,
                "extras": {"client::display": {"contentType": "text/markdown"}}
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                print(f"Successfully sent reminder for task {task_id} to Gotify.")
            else:
                print(f"Error sending reminder for task {task_id}. Gotify responded with {response.status_code}.")

        except Exception as e:
            print(f"An unexpected error occurred while sending reminder for task {task_id}: {e}")

def execute_send(task_id: str):
    """
A self-contained function for the scheduler to call.
    It initializes everything it needs to send a notification.
    """
    print(f"--- REMINDER TRIGGERED for task {task_id} ---")
    store = None
    try:
        config = load_config()
        store = TaskStore(config.task_store_db_path, check_same_thread=True) # Schedulers run in their own threads
        sender = _GotifySenderInternal(config, store)
        sender.send(task_id)
    finally:
        if store:
            store.close()
