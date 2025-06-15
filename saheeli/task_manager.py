"""In-memory task queue management."""

from dataclasses import dataclass

from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from .utils import generate_id


class TaskStatus(str, Enum):
    """Enumerated states for tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


@dataclass
class Task:
    """Data model describing a work item."""

    task_id: str
    prompt: Path
    status: TaskStatus


class TaskManager:
    """Simple in-memory implementation of a task queue."""

    def __init__(self) -> None:
        """Initialise an empty task dictionary."""
        self.tasks: Dict[str, Task] = {}

    def add_task(self, prompt: Path) -> str:
        """Create a new pending task and return its ID."""
        task_id = generate_id()
        self.tasks[task_id] = Task(task_id, prompt, TaskStatus.PENDING)
        return task_id

    def next_task(self) -> Optional[Task]:
        """Return the next pending task if available."""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        """Update the status of a given task."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status

    def list_tasks(self) -> List[Task]:
        """Return all known tasks."""
        return list(self.tasks.values())
