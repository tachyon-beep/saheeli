from pathlib import Path
from pydantic import BaseModel, ValidationError
from .toolbox import Toolbox
from .llm_interface import LLMInterface


class ToolCommand(BaseModel):
    tool: str
    args: dict


class ServoAgent:
    def __init__(self, task_id: str, workspace: Path, llm: LLMInterface) -> None:
        self.task_id = task_id
        self.workspace = workspace
        self.llm = llm
        self.toolbox = Toolbox(workspace)
        self.messages = []

    async def run(self) -> None:
        prompt = (self.workspace / "prompt.md").read_text()
        self.messages.append({"role": "user", "content": prompt})
        while True:
            resp = await self.llm.chat(self.messages)
            try:
                cmd = self.validate_response(resp)
            except ValidationError as e:
                self.messages.append({"role": "system", "content": str(e)})
                continue
            done = await self.handle_response(cmd)
            if done:
                break

    def validate_response(self, payload: dict) -> ToolCommand:
        return ToolCommand.parse_obj(payload)

    async def handle_response(self, command: ToolCommand) -> bool:
        tool = getattr(self.toolbox, command.tool)
        result = tool(**command.args)
        self.messages.append({"role": "system", "content": str(result)})
        return command.tool == "task_complete"
