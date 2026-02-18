# Task Tracker CLI https://roadmap.sh/projects/task-tracker

A command-line task management tool built with Python, Typer, and Rich. 

## Installation

```bash
# Clone the repo
git clone https://github.com/trollerxoxo/task-tracker-cli.git
cd task-tracker-cli

# Install with uv
uv sync
```

## Usage

### Add a task
```bash
task-cli add "Buy groceries"
# Output: Task added successfully: (ID: 1)
```

### List all tasks
```bash
task-cli list
```

### List tasks by status
```bash
task-cli list --status done
task-cli list --status todo
task-cli list --status in-progress
```

### Update a task
```bash
task-cli update 1 --description "Buy groceries and cook dinner"
task-cli update 1 --status done
```

### Delete a task
```bash
task-cli delete 1
```

### Mark task status
```bash
task-cli mark-done 1
task-cli mark-in-progress 1
```

## Task Properties

| Property | Description |
|---|---|
| `id` | Unique identifier |
| `description` | Short description |
| `status` | `todo`, `in-progress`, or `done` |
| `created_at` | Date and time created |
| `updated_at` | Date and time last updated |

## Tech Stack

- **Python 3.12**
- **Typer** — CLI framework
- **Rich** — Terminal formatting
- **SQLModel/Pydantic** — Data validation
- **pytest** — Testing
- **GitHub Actions** — CI/CD

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run the CLI directly
uv run task-cli --help
```

## Project Structure

```
src/task_cli/
├── models.py    # Task model and Status enum
├── storage.py   # JSON file I/O
├── service.py   # Business logic
└── main.py      # CLI commands
tests/
├── test_service.py  # Service layer tests
└── test_main.py     # CLI integration tests
```
