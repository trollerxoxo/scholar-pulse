from .storage import load_tasks, save_tasks
from .models import Task, Status
from typing import List
from datetime import datetime

def add_task(description: str) -> Task:
    tasks = load_tasks()
    if not tasks:
        last_id = 0
    else:
        last_id = max(task.id for task in tasks)

    task = Task(id=last_id + 1, description=description)
    tasks.append(task)
    save_tasks(tasks)

    return task

def get_tasks(status: Status | None = None  ) -> List[Task]:
    tasks = load_tasks()
    if status:
        tasks = [task for task in tasks if task.status == status]
    return tasks

def delete_task(task_id: int) -> Task:
    tasks = load_tasks()
    task_to_delete = next((task for task in tasks if task.id == task_id), None)
    if not task_to_delete:
        raise ValueError(f"Task with id {task_id} not found")
    else:
        tasks = [task for task in tasks if task.id != task_id]
        save_tasks(tasks)
        return task_to_delete

def update_task(task_id: int, description: str | None = None, status: Status | None = None) -> Task:
    tasks = load_tasks()
    task_to_update = next((task for task in tasks if task.id == task_id), None)
    if not task_to_update:
        raise ValueError(f"Task with id {task_id} not found")
    if description:
        task_to_update.description = description
    if status:
        task_to_update.status = status
    task_to_update.updated_at = datetime.now()
    save_tasks(tasks)
    return task_to_update