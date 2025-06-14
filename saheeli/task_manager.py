from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from .utils import generate_id


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


@dataclass
class Task:
    task_id: str
    prompt: Path
    status: TaskStatus


class TaskManager:
    def __init__(self) -> None:
        self.tasks: Dict[str, Task] = {}

    def add_task(self, prompt: Path) -> str:
        task_id = generate_id()
        self.tasks[task_id] = Task(task_id, prompt, TaskStatus.PENDING)
        return task_id

    def next_task(self) -> Optional[Task]:
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def update_status(self, task_id: str, status: TaskStatus) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = status

    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())
