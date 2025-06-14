from pathlib import Path
import subprocess
from .utils import write_json


class Toolbox:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    def _resolve(self, path: str) -> Path:
        return self.workspace / path

    def execute_shell(self, command: str) -> dict:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }

    def create_file(self, path: str, content: str) -> dict:
        file_path = self._resolve(path)
        file_path.write_text(content)
        return {"created": str(file_path)}

    def read_file(self, path: str) -> dict:
        data = self._resolve(path).read_text()
        return {"content": data}

    def edit_file(self, path: str, content: str) -> dict:
        file_path = self._resolve(path)
        file_path.write_text(content)
        return {"edited": str(file_path)}

    def list_files(self, path: str = ".") -> dict:
        base = self._resolve(path)
        return {"files": [p.name for p in base.iterdir()]}

    def task_complete(self, message: str) -> dict:
        write_json(self.workspace / "complete.json", {"message": message})
        return {"complete": True}
