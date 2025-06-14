"""Command line interface for managing Saheeli tasks."""

from pathlib import Path
import typer
from .config import load_config
from .orchestrator import SaheeliOrchestrator

app = typer.Typer(help="Saheeli CLI")
task_app = typer.Typer(help="Task commands")
app.add_typer(task_app, name="task")


@app.command()
def build_servo() -> None:
    """Build the Servo Docker image."""
    cfg = load_config()
    orchestrator = SaheeliOrchestrator(cfg)
    orchestrator.build_servo_image()


@task_app.command("submit")
def submit(prompt: Path = typer.Option(..., exists=True)) -> None:
    """Submit a prompt file and launch the task."""
    cfg = load_config()
    orchestrator = SaheeliOrchestrator(cfg)
    task_id = orchestrator.submit_task(prompt)
    typer.echo(f"Task {task_id} submitted")
    orchestrator.launch_next_task()


@task_app.command("status")
def status() -> None:
    """Display the status of all tasks."""
    cfg = load_config()
    orchestrator = SaheeliOrchestrator(cfg)
    for task in orchestrator.get_status():
        typer.echo(f"{task.task_id}: {task.status}")


if __name__ == "__main__":
    app()
