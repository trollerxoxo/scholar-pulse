from typer.testing import CliRunner
from task_cli.main import app
import pytest
from task_cli.service import add_task, get_tasks, delete_task, update_task
from datetime import datetime

runner = CliRunner()

def test_add_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    result = runner.invoke(app, ["add", "Buy groceries"])
    assert result.exit_code == 0
    assert "Task added successfully: (ID: 1)" in result.output

def test_list_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.output
    assert "todo" in result.output
    assert "1" in result.output

def test_delete_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
    assert "Task deleted successfully: (ID: 1)" in result.output

def test_update_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["update", "1", "--description", "Updated groceries"])
    assert result.exit_code == 0
    assert "Task updated successfully: (ID: 1) (Status: todo)" in result.output

def test_update_command_no_options(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["update", "1"])
    assert result.exit_code == 0
    assert "Description or status must be provided" in result.output

def test_update_command_status(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["update", "1", "--status", "done"])
    assert result.exit_code == 0
    assert "Task updated successfully: (ID: 1) (Status: done)" in result.output 

def test_update_command_invalid_status(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["update", "1", "--status", "invalid"])
    assert result.exit_code != 0  

def test_update_non_existent_id_crashes(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    result = runner.invoke(app, ["update", "999", "--description", "Updated groceries"])
    assert result.exit_code != 0

def test_list_filtered_by_status(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    runner.invoke(app, ["update", "1", "--status", "done"])
    result = runner.invoke(app, ["list", "--status", "done"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.output

def test_list_filtered_by_status_todo(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["list", "--status", "todo"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.output

def test_list_filtered_by_status_no_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "test"])
    runner.invoke(app, ["update", "1", "--status", "done"])
    result = runner.invoke(app, ["list", "--status", "todo"])
    assert result.exit_code == 0
    assert "test" not in result.output

def test_mark_done_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["mark-done", "1"])
    assert result.exit_code == 0
    assert "Task marked as done: (ID: 1) (Status: done)" in result.output

def test_mark_in_progress_command(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["mark-in-progress", "1"])
    assert result.exit_code == 0
    assert "Task marked as in-progress: (ID: 1) (Status: in-progress)" in result.output

def test_list_shows_created_at(tmp_path, monkeypatch):
    monkeypatch.setattr("task_cli.storage.DATA_FILE", tmp_path / "tasks.json")
    runner.invoke(app, ["add", "Buy groceries"])
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Buy groceries" in result.output
    assert "todo" in result.output
    assert "1" in result.output
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    assert today in result.output