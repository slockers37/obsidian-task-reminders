import time
from dotenv import load_dotenv

load_dotenv()

from config import load_config
from watcher import VaultWatcher
from task_store import TaskStore
from scheduler import ReminderScheduler

def main():
    """
    Main function to start the Obsidian Task Reminder system.
    """
    store = None
    scheduler = None
    watcher = None
    try:
        # Load configuration
        config = load_config()
        print("Configuration loaded successfully.")

        # Initialize TaskStore
        store = TaskStore(config.task_store_db_path, check_same_thread=False)
        store.create_schema()
        print("Task store initialized.")

        # Initialize Scheduler
        scheduler = ReminderScheduler(config.scheduler_db_path)
        scheduler.start()
        print("Scheduler started.")

        # Initialize and start the watcher
        watcher = VaultWatcher(
            vault_path=config.vault_path, 
            task_store_db_path=config.task_store_db_path,
            scheduler=scheduler
        )
        watcher.start()

        # Keep the main thread alive
        print("\nApplication is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
            
    except (ValueError, FileNotFoundError) as e:
        print(f"Error during setup: {e}")
        print("Please ensure config.yml, .env, and vault_path are correct.")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if watcher:
            watcher.stop()
        if scheduler:
            scheduler.stop()
            print("Scheduler stopped.")
        if store:
            store.close()
            print("Task store closed.")
        print("Application stopped.")

if __name__ == "__main__":
    main()
