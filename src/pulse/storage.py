import json
from pathlib import Path
from typing import List

from .models import Task

DATA_FILE = Path.home() / ".task_tracker" / "tasks.json"
if not DATA_FILE.exists():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_tasks() -> List[Task]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        return [Task.model_validate(task) for task in json.load(f)]

def save_tasks(tasks: List[Task]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump([task.model_dump(mode='json') for task in tasks], f, indent=4)