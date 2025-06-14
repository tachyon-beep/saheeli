"""Async agent implementation running inside a Servo container."""

from pathlib import Path
import json
from pydantic import BaseModel, ValidationError
from .toolbox import Toolbox
from .llm_interface import LLMInterface
from .utils import read_json, write_json


class ToolCommand(BaseModel):
    """Schema for LLM responses."""

    tool: str
    args: dict


class ServoAgent:
    """Agentic loop orchestrating tool execution."""

    def __init__(self, task_id: str, workspace: Path, llm: LLMInterface) -> None:
        """Initialise the agent for a specific task."""
        self.task_id = task_id
        self.workspace = workspace
        self.llm = llm
        self.toolbox = Toolbox(workspace)
        self.messages = []
        self.log_path = workspace / f"servo-{task_id}-audit.log"
        self.session_path = workspace / f"servo-{task_id}-session.json"
        self.scratchpad_path = workspace / "scratchpad.json"
        if self.scratchpad_path.exists():
            self.scratchpad = read_json(self.scratchpad_path)
        else:
            self.scratchpad = {"history": []}
        self.log_path.write_text("")
        self.max_messages = 50

    def _save_scratchpad(self) -> None:
        """Persist the scratchpad state to disk."""
        write_json(self.scratchpad_path, self.scratchpad)

    def _prune_messages(self) -> None:
        """Move old chat messages to the scratchpad."""
        if len(self.messages) > self.max_messages:
            excess = len(self.messages) - self.max_messages
            removed = self.messages[:excess]
            self.messages = self.messages[excess:]
            self.scratchpad.setdefault("history", []).extend(removed)
            self._save_scratchpad()

    async def run(self) -> None:
        """Main interaction loop with the LLM."""
        prompt = (self.workspace / "prompt.md").read_text()
        self.messages.append({"role": "user", "content": prompt})
        self._log({"role": "user", "content": prompt})
        self._prune_messages()
        while True:
            resp = await self.llm.chat(self.messages)
            self._log({"role": "assistant", "content": resp})
            try:
                cmd = self.validate_response(resp)
            except ValidationError as e:
                err = str(e)
                self.messages.append({"role": "system", "content": err})
                self._log({"role": "error", "content": err})
                self._prune_messages()
                continue
            done = await self.handle_response(cmd)
            if done:
                break
        self.session_path.write_text(json.dumps(self.messages, indent=2))
        self._save_scratchpad()

    def _log(self, entry: dict) -> None:
        """Append an entry to the audit log."""
        with self.log_path.open("a") as f:
            f.write(json.dumps(entry))
            f.write("\n")

    def validate_response(self, payload: dict) -> ToolCommand:
        """Validate LLM output and return a tool command."""
        return ToolCommand.parse_obj(payload)

    async def handle_response(self, command: ToolCommand) -> bool:
        """Execute a tool command and return True if the task completed."""
        tool = getattr(self.toolbox, command.tool)
        result = tool(**command.args)
        self.messages.append({"role": "system", "content": str(result)})
        self._log({"tool_result": result})
        self._prune_messages()
        return command.tool == "task_complete"
