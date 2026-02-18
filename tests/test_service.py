from task_cli.service import add_task, get_tasks, delete_task, update_task
import pytest
from task_cli.models import Status

def test_add_task(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"
    assert tasks[0].status == Status.TODO
    assert tasks[0].id == 1

def test_id_increments(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    add_task("Learn Python")
    delete_task(2)
    add_task("Learn Rust")
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].id == 1
    assert tasks[1].id == 2

def test_get_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    add_task("Learn Python")
    tasks = get_tasks()
    assert len(tasks) == 2
    assert tasks[0].description == "Buy groceries"
    assert tasks[0].status == Status.TODO
    assert tasks[0].id == 1
    assert tasks[1].description == "Learn Python"
    assert tasks[1].status == Status.TODO
    assert tasks[1].id == 2

def test_get_tasks_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    tasks = get_tasks()
    assert len(tasks) == 0
    assert tasks == []

def test_delete_task(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    delete_task(1)
    tasks = get_tasks()
    assert len(tasks) == 0

def test_delete_non_existent_task_raises_error(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    with pytest.raises(ValueError):
        delete_task(999)

def test_update_task_description(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    updated_task = update_task(1, "Learn Python")
    assert updated_task.description == "Learn Python"
    assert updated_task.status == Status.TODO
    assert updated_task.id == 1

def test_update_task_status(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    updated_task = update_task(1, status=Status.DONE)
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"
    assert tasks[0].status == Status.DONE
    assert tasks[0].id == 1

def test_update_task_status_and_description(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    update_task(1, "Learn Python", Status.DONE)
    tasks = get_tasks()
    assert len(tasks) == 1
    assert tasks[0].description == "Learn Python"
    assert tasks[0].status == Status.DONE
    assert tasks[0].id == 1

def test_update_non_existent_task_raises_error(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    with pytest.raises(ValueError):
        update_task(999, "Learn Python", Status.DONE)

def test_created_at_and_updated_at_are_set(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    tasks = get_tasks()
    assert tasks[0].created_at is not None
    assert tasks[0].updated_at is not None

def test_updated_at_is_updated(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    add_task("Buy groceries")
    update_task(1, "Learn Python")
    tasks = get_tasks()
    assert tasks[0].updated_at > tasks[0].created_at