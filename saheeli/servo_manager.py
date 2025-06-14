"""Management of Servo Docker containers."""

from pathlib import Path
import docker
import os
from .config import Config


class ServoManager:
    """Build and run Servo containers."""

    def __init__(self, config: Config) -> None:
        """Create a manager bound to the given configuration."""
        self.config = config
        self.client = docker.from_env()

    def build_image(self) -> None:
        """Build the Docker image for Servos."""
        self.client.images.build(path=".", tag=self.config.servo_image)

    def run_servo(
        self, task_id: str, prompt: Path, workspace: Path
    ) -> docker.models.containers.Container:
        """Start a Servo container for the given task."""
        volumes = {
            prompt.resolve(): {"bind": "/workspace/prompt.md", "mode": "ro"},
            workspace.resolve(): {"bind": "/workspace", "mode": "rw"},
        }
        env = {
            self.config.api_key_env_var: os.getenv(self.config.api_key_env_var, ""),
            "TASK_ID": task_id,
        }
        container = self.client.containers.run(
            self.config.servo_image,
            detach=True,
            volumes=volumes,
            environment=env,
            cpu_period=100000,
            cpu_quota=int(self.config.cpu_limit * 100000),
            mem_limit=self.config.memory_limit,
        )
        return container

    def copy_workspace(
        self, container: docker.models.containers.Container, dest: Path
    ) -> None:
        """Archive the container workspace to the host."""
        bits, _ = container.get_archive("/workspace")
        dest.mkdir(parents=True, exist_ok=True)
        with open(dest / "workspace.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)

    def remove_container(self, container: docker.models.containers.Container) -> None:
        """Force remove a container, ignoring missing ones."""
        try:
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def wait_for_exit(self, container: docker.models.containers.Container) -> int:
        """Wait for the container to exit and return its status code."""
        result = container.wait(timeout=self.config.timeout)
        return result.get("StatusCode", 1)

    def check_complete(self, workspace: Path) -> bool:
        """Return True if the task completed successfully."""
        return (workspace / "complete.json").exists()
