import pytest
from parser import parse_tasks
from datetime import datetime

def test_parse_single_valid_task():
    content = "- [ ] Buy milk ⏰ 18:30 📅 2025-09-18"
    tasks = parse_tasks(content)
    assert len(tasks) == 1
    task = tasks[0]
    assert task['text'] == "Buy milk"
    assert task['due'] == datetime(2025, 9, 18, 18, 30)
    assert not task['completed']

def test_parse_completed_task():
    content = "- [x] Buy milk ⏰ 18:30 📅 2025-09-18"
    tasks = parse_tasks(content)
    assert len(tasks) == 1
    task = tasks[0]
    assert task['completed']

def test_no_tasks_in_content():
    content = "This is a regular line of text."
    tasks = parse_tasks(content)
    assert len(tasks) == 0

def test_task_without_due_date():
    content = "- [ ] A task without a due date."
    tasks = parse_tasks(content)
    assert len(tasks) == 1
    task = tasks[0]
    assert task['text'] == "A task without a due date."
    assert task['due'] is None

def test_multiple_tasks():
    content = """
- [ ] Task 1 ⏰ 10:00 📅 2025-10-20
- [ ] Task 2
- [x] Completed Task 3 ⏰ 12:00 📅 2025-10-21
    """
    tasks = parse_tasks(content)
    assert len(tasks) == 3
    assert tasks[0]['text'] == "Task 1"
    assert tasks[0]['due'] == datetime(2025, 10, 20, 10, 0)
    assert not tasks[0]['completed']
    assert tasks[1]['text'] == "Task 2"
    assert tasks[1]['due'] is None
    assert not tasks[1]['completed']
    assert tasks[2]['text'] == "Completed Task 3"
    assert tasks[2]['due'] == datetime(2025, 10, 21, 12, 0)
    assert tasks[2]['completed']
