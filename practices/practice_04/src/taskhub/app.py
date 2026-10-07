from __future__ import annotations

from pathlib import Path
from typing import Optional, List

import typer

from .models import Task
from .storage import Storage
 


app = typer.Typer(add_completion=False, help="TaskHub CLI")



def get_storage(root: Optional[str] = None) -> Storage:
    base = Path(root or ".").resolve()
    st = Storage(base)
    st.init()
    return st


@app.command()
def init(root: Optional[str] = typer.Option(None, help="Project root for storage")):
    """Initialize storage (creates tasks.json)."""
    st = get_storage(root)
    typer.echo(f"Initialized storage at {st.path}")


@app.command()
def add(
    title: str,
    due: Optional[str] = typer.Option(None),
    tag: Optional[str] = typer.Option(None, "--tag"),
):
    """Add a new task with optional due date and tags."""
    st = get_storage()
    tags = [tag] if tag else []
    task = Task.new(title=title, due_date=due, tags=tags)
    st.add_task(task)
    typer.echo(task.id)


@app.command()
def list(
    status: Optional[str] = typer.Option(None, help="Filter by status: todo|done"),
    tag: Optional[str] = typer.Option(None, help="Filter by tag"),
):
    """List tasks, optionally filtered."""
    st = get_storage()
    tasks = st.list_tasks(status=status, tag=tag)
    for t in tasks:
        tags = ",".join(t.tags)
        typer.echo(f"{t.id} [{t.status}] {t.title} (due={t.due_date or '-'} tags={tags})")


@app.command()
def done(task_id: str):
    """Mark a task as done by id."""
    st = get_storage()
    t = st.mark_done(task_id)
    if not t:
        raise typer.Exit(code=1)
    typer.echo(f"done {t.id}")


if __name__ == "__main__":
    app()
