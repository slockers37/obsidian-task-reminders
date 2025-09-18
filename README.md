# Obsidian Task Reminders

This project appears to be a Python application designed to manage and send reminders for tasks, likely integrated with Obsidian. It includes components for parsing tasks, scheduling, sending notifications (possibly via Gotify), and storing task data.

## Features (Inferred)

*   **Task Parsing:** Reads and interprets task definitions.
*   **Task Scheduling:** Schedules reminders based on task due dates or other criteria.
*   **Notification Sending:** Sends notifications, potentially through services like Gotify.
*   **Task Storage:** Manages a persistent store for tasks.
*   **File Watching:** Monitors relevant files for changes to update tasks.
*   **Configurable:** Uses a `config.yml` for various settings.
*   **Docker Support:** Can be run using Docker and Docker Compose.

## Setup

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/obsidian-task-reminders.git
    cd obsidian-task-reminders
    ```
2.  **Install dependencies using `uv`:**
    ```bash
    uv sync
    ```
3.  **Create your configuration file:**
    Copy `config.sample.yml` to `config.yml` and adjust settings as needed.
    ```bash
    cp config.sample.yml config.yml
    ```
    Ensure you set any sensitive information (like `GOTIFY_TOKEN`) via environment variables, as specified in `config.yml`.

### Docker

1.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    You might need to create a `config.yml` and `.env` file in the project root, similar to the local setup, for Docker to pick up your specific configurations.

## Configuration

The application uses `config.yml` for its settings. A `config.sample.yml` is provided as a template. Key configuration options include:

*   `vault_path`: Path to your Obsidian vault.
*   `timezone`: Timezone for scheduling.
*   `gotify`: Gotify server URL and token (token should be an environment variable).
*   `retry`: Settings for retrying operations.
*   `database`: Paths for task store and scheduler databases.

**Important:** For sensitive information like API tokens, it is recommended to use environment variables (e.g., `GOTIFY_TOKEN`) instead of hardcoding them directly in `config.yml`.

## Usage

To run the application locally:

```bash
uv run src/main.py
```

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the [License Name] - see the LICENSE file for details.
