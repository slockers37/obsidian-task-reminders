import re
from datetime import datetime

TASK_REGEX = re.compile(r"^\s*-\s*\[( |x)\]\s*(.*?)(?:\s*⏰\s*(\d{2}:\d{2}))?(?:\s*📅\s*(\d{4}-\d{2}-\d{2}))?\s*$")

def parse_tasks(content: str) -> list[dict]:
    tasks = []
    for line in content.splitlines():
        match = TASK_REGEX.match(line)
        if match:
            completed_char, text, time_str, date_str = match.groups()
            
            due = None
            if date_str and time_str:
                try:
                    due = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                except ValueError:
                    # Handle cases where date or time might be malformed, though regex should prevent this.
                    pass

            tasks.append({
                "text": text.strip(),
                "completed": completed_char == 'x',
                "due": due,
                "raw_line": line, # Good to keep for later, e.g. for writing back
            })
    return tasks
