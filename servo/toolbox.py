from __future__ import annotations

import json
import os
import csv
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

import httpx

from .utils import read_json, write_json


class Toolbox:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.scratchpad_path = workspace / "scratchpad.json"

    def _resolve(self, path: str) -> Path:
        return self.workspace / path

    # Scratchpad helpers
    def _read_scratchpad(self) -> dict:
        if self.scratchpad_path.exists():
            return read_json(self.scratchpad_path)
        return {}

    def _write_scratchpad(self, data: dict) -> None:
        write_json(self.scratchpad_path, data)

    # ------------------------------------------------------------------
    # File system & archive operations
    def list_files(self, path: str = ".", recursive: bool = False) -> dict:
        base = self._resolve(path)
        if recursive:
            files = [str(p.relative_to(self.workspace)) for p in base.rglob("*")]
        else:
            files = [p.name for p in base.iterdir()]
        return {"status": "ok", "files": files}

    def create_file(self, path: str, content: str = "") -> dict:
        file_path = self._resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return {"status": "ok", "created": str(file_path)}

    def read_file(self, path: str) -> dict:
        data = self._resolve(path).read_text()
        return {"status": "ok", "content": data}

    def edit_file(
        self, path: str, start_line: int, end_line: int, new_content: str
    ) -> dict:
        file_path = self._resolve(path)
        lines = file_path.read_text().splitlines()
        lines[start_line - 1 : end_line] = new_content.splitlines()
        file_path.write_text("\n".join(lines) + "\n")
        return {"status": "ok", "edited": str(file_path)}

    def delete_file(self, path: str) -> dict:
        file_path = self._resolve(path)
        if file_path.is_dir():
            file_path.rmdir()
        else:
            file_path.unlink(missing_ok=True)
        return {"status": "ok"}

    def text_search(
        self, query: str, path: str = ".", case_sensitive: bool = False
    ) -> dict:
        base = self._resolve(path)
        matches = []
        for file in base.rglob("*"):
            if file.is_file():
                data = file.read_text(errors="ignore")
                haystack = data if case_sensitive else data.lower()
                needle = query if case_sensitive else query.lower()
                if needle in haystack:
                    matches.append(str(file.relative_to(self.workspace)))
        return {"status": "ok", "matches": matches}

    def create_archive(
        self, archive_path: str, source_paths: List[str], format: str = "zip"
    ) -> dict:
        archive_file = self._resolve(archive_path)
        root = archive_file.with_suffix("")
        base_dir = self._resolve(".")
        shutil.make_archive(str(root), format, base_dir, base_dir)
        return {"status": "ok", "archive": str(archive_file)}

    def extract_archive(self, archive_path: str, destination_path: str) -> dict:
        archive = self._resolve(archive_path)
        dest = self._resolve(destination_path)
        dest.mkdir(parents=True, exist_ok=True)
        shutil.unpack_archive(str(archive), str(dest))
        return {"status": "ok", "destination": str(dest)}

    # ------------------------------------------------------------------
    # Code, execution & version control
    def execute_shell(self, command: str, timeout: int = 60) -> dict:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }

    def lint_code(self, path: str) -> dict:
        proc = subprocess.run(["ruff", path], capture_output=True, text=True)
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def run_tests(self, test_path: str = "tests/") -> dict:
        proc = subprocess.run(["pytest", test_path], capture_output=True, text=True)
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def package_install(self, packages: List[str], manager: str = "pip") -> dict:
        if manager == "pip":
            cmd = ["pip", "install", *packages]
        else:
            cmd = ["apt-get", "install", "-y", *packages]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def git_clone(self, repo_url: str, destination_path: str) -> dict:
        proc = subprocess.run(
            ["git", "clone", repo_url, destination_path], capture_output=True, text=True
        )
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def git_commit(self, message: str, add_all: bool = True) -> dict:
        if add_all:
            subprocess.run(["git", "add", "-A"])
        proc = subprocess.run(
            ["git", "commit", "-m", message], capture_output=True, text=True
        )
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def git_diff(self, cached: bool = False) -> dict:
        cmd = ["git", "diff"]
        if cached:
            cmd.append("--cached")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return {"status": "ok", "stdout": proc.stdout}

    # ------------------------------------------------------------------
    # Networking & Internet Access
    def http_get(self, url: str, destination_path: Optional[str] = None) -> dict:
        client = httpx.Client()
        resp = client.get(url)
        resp.raise_for_status()
        if destination_path:
            dest = self._resolve(destination_path)
            dest.write_bytes(resp.content)
            return {"status": "ok", "path": str(dest)}
        return {"status": "ok", "content": resp.text}

    def search_web(self, query: str) -> dict:
        url = "https://duckduckgo.com/html/"
        resp = httpx.get(url, params={"q": query})
        return {"status": "ok", "content": resp.text[:500]}

    def make_api_call(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        client = httpx.Client()
        resp = client.request(method, url, params=params, json=json_data)
        return {"status": "ok", "status_code": resp.status_code, "content": resp.text}

    # ------------------------------------------------------------------
    # Data & Document Processing
    def parse_structured_data(self, path: str) -> dict:
        file_path = self._resolve(path)
        if file_path.suffix == ".json":
            return {"status": "ok", "data": json.loads(file_path.read_text())}
        if file_path.suffix == ".csv":
            with file_path.open() as f:
                reader = csv.DictReader(f)
                return {"status": "ok", "data": list(reader)}
        return {"status": "error", "message": "unsupported format"}

    def run_notebook(self, path: str) -> dict:
        proc = subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                path,
                "--output",
                path,
            ],
            capture_output=True,
            text=True,
        )
        return {"status": "ok", "stdout": proc.stdout, "stderr": proc.stderr}

    def convert_document(self, source_path: str, output_format: str) -> dict:
        dest = self._resolve(source_path).with_suffix("." + output_format)
        proc = subprocess.run(
            [
                "pandoc",
                self._resolve(source_path),
                "-o",
                dest,
            ],
            capture_output=True,
            text=True,
        )
        return {
            "status": "ok",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "path": str(dest),
        }

    def summarize_document(self, path: str) -> dict:
        text = self._resolve(path).read_text()
        summary = text[:200]
        return {"status": "ok", "summary": summary}

    # ------------------------------------------------------------------
    # System Introspection & Session Management
    def list_processes(self) -> dict:
        proc = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        return {"status": "ok", "processes": proc.stdout}

    def get_system_metrics(self) -> dict:
        usage = shutil.disk_usage(self.workspace)
        load = os.getloadavg()[0]
        return {
            "status": "ok",
            "disk_total": usage.total,
            "disk_used": usage.used,
            "loadavg": load,
        }

    def add_to_scratchpad(self, key: str, value: str) -> dict:
        data = self._read_scratchpad()
        data[key] = value
        self._write_scratchpad(data)
        return {"status": "ok"}

    # ------------------------------------------------------------------
    # Agent Meta-Cognition & Task Management
    def spawn_child_servo(self, prompt_file_path: str) -> dict:
        req_path = self.workspace / "spawn_child.json"
        write_json(req_path, {"prompt": prompt_file_path})
        return {"status": "ok", "request": str(req_path)}

    def task_complete(self, summary: str) -> dict:
        write_json(self.workspace / "complete.json", {"summary": summary})
        return {"status": "ok", "complete": True}
