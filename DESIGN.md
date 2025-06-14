# Saheeli Design Document

## 1. Chosen Technology Stack

- **Python 3.12**
- **CLI**: [Typer](https://typer.tiangolo.com/) for command line interface.
- **Container Management**: [docker SDK for Python](https://docker-py.readthedocs.io/) (`docker`) to build images and run containers.
- **Prompt Parsing**: [`PyYAML`](https://pyyaml.org/) for YAML front-matter, [`markdown-it-py`](https://github.com/executablebooks/markdown-it-py) for optional markdown parsing.
- **LLM Interface**: Uses the `httpx` asynchronous client for API communication, with all responses validated by `pydantic` models.
- **Async Execution**: Servo agents run inside an `asyncio` event loop to await LLM responses without blocking.
- **Configuration**: [`pydantic`](https://docs.pydantic.dev/) for typed config models loaded from `config.yaml` or environment variables.
- **Logging**: Python `logging` module writing JSON lines.

## 2. Proposed File Structure

```
saheeli/
├── saheeli/                # Foreman package
│   ├── __init__.py
│   ├── cli.py              # Typer CLI entry points
│   ├── orchestrator.py     # SaheeliOrchestrator core logic
│   ├── servo_manager.py    # Build/run Servo containers
│   ├── task_manager.py     # Queue and status tracking
│   ├── config.py           # Config models and loading helpers
│   └── utils.py
├── servo/                  # Servo agent package
│   ├── __init__.py
│   ├── main.py             # Entry point when container starts
│   ├── agent.py            # ServoAgent loop implementation
│   ├── llm_interface.py    # LLM API wrapper
│   ├── toolbox.py          # Tool definitions
│   └── utils.py
├── prompts/                # Example prompts for validation
├── results/                # Collected result directories
├── Dockerfile              # Servo container image
├── requirements.txt
├── requirements-dev.txt
├── config.yaml             # Default config
├── .env.example            # Example environment file
├── README.md
└── DESIGN.md               # This document
```

## 3. Component API Design

### 3.1 SaheeliOrchestrator (saheeli/orchestrator.py)
```python
class SaheeliOrchestrator:
    def __init__(self, config: Config, tasks: TaskManager, servos: ServoManager):
        """Coordinate TaskManager and ServoManager."""
    def build_servo_image(self, tag: str = "saheeli-servo") -> None:
        """Build the Servo Docker image."""
    def submit_task(self, prompt_path: Path) -> str:
        """Add a prompt to the queue and return task ID."""
    def launch_next_task(self) -> None:
        """Start the next task in the queue if resources allow."""
    def get_status(self) -> list[TaskStatus]:
        """Return status of all tasks."""
    def fetch_results(self, task_id: str, dest: Path) -> None:
        """Copy result artifacts for the given task ID."""
```

### 3.2 ServoManager (saheeli/servo_manager.py)
```python
class ServoManager:
    def __init__(self, config: Config):
        ...
    def run_servo(self, task_id: str, prompt_path: Path) -> ServoHandle:
        """Spawn a Servo container with resource limits."""
    def monitor(self, handle: ServoHandle) -> None:
        """Watch the container and check for `/workspace/complete.json` on exit."""
```

### 3.3 TaskManager (saheeli/task_manager.py)
```python
class TaskManager:
    def __init__(self, db_path: Path):
        ...
    def add_task(self, prompt_path: Path) -> str:
        """Return new task ID and mark it as pending."""
    def next_task(self) -> Task | None:
        """Fetch the next pending task if available."""
    def update_status(self, task_id: str, status: TaskStatus) -> None:
        ...
    def list_tasks(self) -> list[Task]:
        ...
```

### 3.4 ServoAgent (servo/agent.py)
```python
class ServoAgent:
    def __init__(self, task_id: str, workspace: Path, config: ServoConfig):
        ...
    async def run(self) -> None:
        """Main async loop: send prompt, await response, validate and handle."""
    def validate_response(self, payload: dict) -> ToolCommand:
        """Use pydantic to parse and validate the LLM response."""
    async def handle_response(self, command: ToolCommand) -> bool:
        """Execute tools and write `complete.json` on success."""
```

### 3.5 LLMInterface (servo/llm_interface.py)
```python
class LLMInterface:
    def __init__(self, api_key: str, model: str):
        ...
    async def chat(self, messages: list[dict]) -> dict:
        """Send a request via `httpx.AsyncClient` and return parsed JSON."""
```

### 3.6 Toolbox (servo/toolbox.py)
```python
class Toolbox:
    def __init__(self, workspace: Path):
        ...
    def execute_shell(self, command: str) -> dict:
        ...
    def create_file(self, path: str, content: str) -> dict:
        ...
    def read_file(self, path: str) -> dict:
        ...
    def edit_file(self, path: str, content: str) -> dict:
        ...
    def list_files(self, path: str = ".") -> dict:
        ...
    def task_complete(self, message: str) -> dict:
        ...  # writes `/workspace/complete.json`
```

## 4. Communication Protocol

1. **Image Build**: `saheeli build-servo` creates or updates the Servo Docker image.
2. **Task Submission**: User runs `saheeli task submit --prompt <file>`.
3. **Task Queue**: Saheeli assigns a unique `task_id` and places it in a queue.
4. **Servo Launch**: Saheeli spawns a Docker container running `servo/main.py`.
   - Mounts prompt file to `/workspace/prompt.md`.
   - Mounts a host results directory to `/workspace/results`.
5. **Servo Execution**:
  - Servo reads `prompt.md`, starts agentic loop.
  - It writes logs to `/workspace/servo-<task_id>-audit.log` and session to `servo-<task_id>-session.json`.
  - On `task_complete`, `Toolbox.task_complete` writes `/workspace/complete.json` then the Servo exits.
   - If the file exists, the task is marked `complete`; this file is Saheeli's definitive success signal.
   - Regardless, Saheeli copies the entire `/workspace` to `results/<task_id>/` on the host.
6. **Status Reporting**: `saheeli task status` inspects queued/running/completed tasks and prints summary info.

## 5. Error Recovery Strategy

- If a Servo container exits without creating `/workspace/complete.json` (non-zero exit or timeout):
  1. Saheeli marks the task state as `incomplete`.
  2. The workspace is still copied to `results/<task_id>/` for inspection.
  3. A warning is logged suggesting manual review or re-run.
- Tasks may be retried by submitting the same prompt again, producing a new `task_id`.

