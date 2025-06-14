from pathlib import Path
import docker
from .config import Config


class ServoManager:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = docker.from_env()

    def build_image(self) -> None:
        self.client.images.build(path=".", tag=self.config.servo_image)

    def run_servo(
        self, task_id: str, prompt: Path, workspace: Path
    ) -> docker.models.containers.Container:
        volumes = {
            prompt.resolve(): {"bind": "/workspace/prompt.md", "mode": "ro"},
            workspace.resolve(): {"bind": "/workspace", "mode": "rw"},
        }
        container = self.client.containers.run(
            self.config.servo_image,
            detach=True,
            volumes=volumes,
            cpu_period=100000,
            cpu_quota=int(self.config.cpu_limit * 100000),
            mem_limit=self.config.memory_limit,
        )
        return container

    def copy_workspace(
        self, container: docker.models.containers.Container, dest: Path
    ) -> None:
        bits, _ = container.get_archive("/workspace")
        dest.mkdir(parents=True, exist_ok=True)
        with open(dest / "workspace.tar", "wb") as f:
            for chunk in bits:
                f.write(chunk)

    def remove_container(self, container: docker.models.containers.Container) -> None:
        try:
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def wait_for_exit(self, container: docker.models.containers.Container) -> int:
        result = container.wait(timeout=self.config.timeout)
        return result.get("StatusCode", 1)

    def check_complete(self, workspace: Path) -> bool:
        return (workspace / "complete.json").exists()
