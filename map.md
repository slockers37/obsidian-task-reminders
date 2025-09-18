Below is a careful, end-to-end map of the whole system from the moment you type a task in Obsidian to the moment Gotify pushes the reminder.

# 1. High level components

1. File watcher
   - Watches your vault for file events (create, modify, delete) only for `.md` files.

2. Task parser
   - Extracts tasks and their metadata from a changed file, using your format `- [ ] ... ⏰ HH:MM 📅 YYYY-MM-DD`.

3. Task store / index
   - A small persistent database that maps stable task IDs to scheduled job IDs and stores task metadata (file path, line hash, due datetime, status).

4. Scheduler with persistence
   - Schedules one-shot jobs to run at the exact due time. The scheduler persists jobs so they survive restarts.

5. Gotify sender
   - Sends the notification to your Gotify server when the job fires. Includes retry/backoff and logs success/failure.

6. Optional writer (safe)
   - Optionally marks the task done in the note after sending, if you want automatic completion. Do this carefully and make it opt-in.

7. Supervisor / single-instance guard
   - Ensures only one watcher/scheduler is active for a given vault to avoid duplicate scheduling.

# 2. End-to-end event flows

## A. Startup

1. Acquire single-instance lock (file lock or system lock). If another instance is running, exit or run in read-only mode.
2. Load config (vault path, timezone, Gotify URL/token, retry settings). Ensure GOTIFY_TOKEN is from environment or restricted config.
3. Initialize persistent task store and scheduler jobstore.
4. Do a one-time scan of the vault to build the initial index and schedule all future tasks. Any tasks with due times in the past are handled according to policy (see missed triggers).
5. Start file watcher and scheduler loop.

## B. File changed (create or modify)

1. Watcher receives event for `path/to/note.md`. Apply filters: only `.md`, ignore hidden folders, debounce rapid successive events for same path (for example wait 300–1000 ms to avoid intermediate writes).
2. Parser reads the file and extracts all tasks matching the pattern. For each task produce a parsed record: `{task_text, due_datetime, line_context, maybe inline id}`. Use the configured timezone to create a timezone-aware datetime object.
3. Compare parsed records for that file against task store entries for the same file: compute three sets: new tasks, updated tasks, removed tasks.
   - New tasks: add to task store and schedule a job.
   - Updated tasks: if due time or text changed, update task store and reschedule job (cancel old one then add new).
   - Removed tasks or tasks marked done: cancel scheduled job and mark task as cancelled or done in task store.

4. Log what changed and any scheduling errors.

## C. Task due (scheduler triggers)

1. Scheduler invokes the job. Job code: read task metadata from task store, send message to Gotify with configured payload and headers.
2. On first successful send: update task store status to sent (and optionally add a note to the markdown file to mark complete, depending on config).
3. On failure: retry according to policy with exponential backoff, up to max attempts. After exhausting retries, mark task as failed and optionally alert user via a secondary channel or log.

## D. Task completed manually in Obsidian

1. Watcher sees the file change, parser sees the task now checked or removed.
2. Task store cancels any scheduled job and marks status as completed. No notification is sent if it was cancelled before firing.

# 3. Task identity and idempotency

Reliable mappings between file tasks and scheduled jobs is critical.

Options for stable task IDs:

1. Best: embed a stable ID in the task line, for example add a short UUID tag like `#remid:abcd1234` (recommended). This makes updates and deletes deterministic.
2. If you cannot modify notes: derive a best-effort ID from `hash(file path + line start context + N chars)`. Drawback: inserting lines above will shift line offsets, and editing text will change the hash. Handle by allowing fuzzy matching on edit: attempt to match by previous stored hashes with some tolerance, then treat as updated rather than new.

Task store fields to persist:

- task_id (stable)
- file_path
- snippet (line context)
- due_datetime (ISO, timezone-aware)
- job_id (scheduler id)
- status (scheduled, sent, cancelled, failed)
- last_seen timestamp
- retries count

# 4. Scheduler and persistence choices

- Use a scheduler that supports persistent job stores so jobs survive restarts. Example jobstore backends: SQLite, Redis, or the scheduler's built-in persistent store. Persisting both the scheduler jobs and your task store prevents lost reminders.
- Configure scheduler options:
  - misfire_grace_time: how long to allow late execution if the app was down.
  - coalesce: whether to combine multiple missed runs. For one-shot reminders, you likely want to run late jobs once rather than coalesce.

- On restart, reconcile jobs in jobstore with the task store and the vault. Cancel orphaned jobs or recreate missing ones according to reconciliation policy.

# 5. Handling missed triggers and downtime

Policy choices you must decide and implement:

- If the host was down at the scheduled time, do you:
  - Send missed reminders immediately on restart, or
  - Skip missed reminders, or
  - List them as missed and let the user decide.

- Practical default: if due < now and within a short grace window (for example within last 24 hours), send immediately. Otherwise mark as expired/missed.

# 6. File watcher robustness details

- Use a robust watcher library that handles cross-platform edge cases, e.g., writes that are temporary files then rename.
- Debounce events per file to avoid reprocessing on atomic editor saves.
- Ignore directories like `.obsidian`, `attachments`, `.git`.
- On rename/move handle as delete + create. Transfer task state intelligently: if filename changed, either cancel old tasks or reassign them by matching snippets.
- For bulk operations (mass renames or git checkouts) provide a manual "rescan" option to rebuild index instead of reacting to thousands of events.

# 7. Gotify send logic and resilience

- Use HTTPS for Gotify if available. Send token in Authorization header or query param as Gotify expects. Do not hardcode token in code. Use environment variable or a restricted config file.
- Payload: include title, full task text, original file path, and a link to file path or line number if you want quick jump.
- Retry policy: exponential backoff with jitter, configurable max retries. Persist failed sends to a retry queue so transient network issues do not lose reminders.
- Log each send attempt and response codes. If Gotify returns 4xx for auth, fail fast and require operator action.

# 8. Optional writeback to Obsidian

- If you want the script to mark the task done in your note after sending:
  - Make writeback optional and configurable per vault.
  - Use a conservative approach: edit the file only if the line matches the stored snippet exactly. Avoid mass rewrites.
  - Keep backups or create a small undo mechanism in case of corruption.

# 9. Concurrency and single-instance

- Only run one active watcher/scheduler for a vault. If multiple machines might access the same vault (network share), protect with a distributed lock or run scheduler only on one machine.
- For multiple servers sending to the same Gotify, ensure deduplication of sends by relying on the task store and job ids.

# 10. Security and privacy

- Store Gotify token in environment variables or OS secret store. File permissions should be restrictive.
- If your vault is synced to cloud, be careful about storing task store database with sensitive content. Keep the store locally on the machine that performs scheduling.
- Use HTTPS for Gotify and validate TLS.

# 11. Monitoring, logs, and visibility

- Keep structured logs for events: scheduled, rescheduled, cancelled, sent, failed.
- Expose a small HTTP health endpoint or CLI to list scheduled reminders, cancel by id, trigger a manual rescan, or force-send.
- Optionally add small web UI to view upcoming reminders.

# 12. Edge cases and examples

- Duplicate tasks: detect near-duplicate text in same file and warn or deduplicate.
- Very large vault: on startup, batch-scan and show progress. Use the watcher approach to avoid repeated full scans.
- Timezone changes: store due datetimes as timezone-aware. Default to vault or system timezone, configurable. India timezone (Asia/Kolkata) does not use DST, but if you or your receivers travel, you may want timezone-aware ISO datetimes.
- Repeated tasks: if you want repeating reminders implement recurrence in task metadata or handle by rescheduling the next occurrence after a job fires.

# 13. Testing and validation

- Unit test the parser with many edge cases: multiple tasks per line, tasks without time, invalid date formats.
- Integration test the end-to-end flow using a local mock Gotify server to verify retries and payloads.
- Simulate watcher events and bulk edits to ensure debounce and reconciliation logic works.

# 14. Deployment recommendations

- For a personal laptop/server: run as a systemd service (Linux) or scheduled background service. Ensure auto-restart on failure.
- If you want containerization: mount the vault into the container and run the service. Use a volume for the persistent task store. Beware of file event propagation differences in container setups.
- Use small resource footprint components: a single Python process with a light scheduler is usually enough.

# 15. Minimal recommended tech stack and config

- Language: Python or node; Python is common and has good libs.
- File watcher: watchdog (Python) or chokidar (node).
- Scheduler: APScheduler with SQLite or Redis jobstore; or a small persistent queue like RQ if you need heavy reliability.
- HTTP client: requests (Python) or node-fetch.
- Storage: SQLite for simple setups, Redis for multi-instance or scaling.
- Config: environment variables for secrets, simple `config.yml` for other settings.

# 16. Concrete example timeline (illustrative)

1. 10:00 You add: `- [ ] Buy milk ⏰ 18:30 📅 2025-09-18` and save `groceries.md`.
2. 10:00 Watcher sees modify event, debounces, parser extracts task due 2025-09-18T18:30 (Asia/Kolkata).
3. 10:00 Task store assigns `task_id=uuid123`, schedules job `job_id=aps-456` with scheduler. Log: scheduled.
4. 18:30 Scheduler triggers job, sender posts to Gotify. Gotify responds 200. Task store marks `sent`. If configured, writer updates the note to `- [x] Buy milk` or appends a note that reminder was sent.
5. 18:31 If Gotify failed due to network, scheduler or sender retries; on permanent failure store marks `failed` and notifies user or logs.

# 17. Quick checklist to implement

- [ ] Decide whether to embed stable task IDs in tasks or rely on best-effort hashing.
- [ ] Choose libraries: watchdog, APScheduler, requests, SQLite.
- [ ] Implement parser, task store, scheduler glue, and Gotify sender.
- [ ] Add debounce and event filtering in watcher.
- [ ] Add persistence and reconciliation on startup.
- [ ] Add secure config management for Gotify token.
- [ ] Add logging, retry, and health endpoints.
- [ ] Test parser and end-to-end with a mock Gotify.
