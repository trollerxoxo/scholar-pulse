import typer
from typing import Annotated, Optional
from . import service
from .models import Status
from rich import print
from rich.table import Table


app = typer.Typer()

@app.command("add")
def add_task(description: Annotated[str, typer.Argument()]):
    added_task = service.add_task(description)
    print(f"Task added successfully: (ID: {added_task.id})")

@app.command("delete")
def delete_task(task_id: Annotated[int, typer.Argument()]):
    deleted_task = service.delete_task(task_id)
    print(f"Task deleted successfully: (ID: {deleted_task.id})")

@app.command("update")
def update_task(task_id: Annotated[int, typer.Argument()], 
            description: Annotated[Optional[str], typer.Option()] = None, 
            status: Annotated[Optional[Status], typer.Option()] = None):
    if description is None and status is None:
        print(":warning: Description or status must be provided")
        return
    updated_task = service.update_task(task_id, description, status)
    print(f"Task updated successfully: (ID: {updated_task.id}) (Status: {updated_task.status})")

@app.command("list")
def list_tasks(status: Annotated[Optional[Status], typer.Option()] = None):
    table = Table(title="Tasks")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Status", justify="right", style="green")  
    table.add_column("Created", justify="right", style="green")
    table.add_column("Updated", justify="right", style="green")
    tasks = service.get_tasks(status=status)
    for task in tasks:
        table.add_row(str(task.id), 
        task.description, 
        task.status, 
        task.created_at.strftime("%Y-%m-%d %H:%M"), 
        task.updated_at.strftime("%Y-%m-%d %H:%M"))
    print(table)

@app.command("mark-done")
def mark_done(task_id: Annotated[int, typer.Argument()]):
    updated_task = service.update_task(task_id, status=Status.DONE)
    print(f"Task marked as done: (ID: {updated_task.id}) (Status: {updated_task.status})")  

@app.command("mark-in-progress")
def mark_in_progress(task_id: Annotated[int, typer.Argument()]):
    updated_task = service.update_task(task_id, status=Status.IN_PROGRESS)
    print(f"Task marked as in-progress: (ID: {updated_task.id}) (Status: {updated_task.status})")

if __name__ == "__main__":
    app()