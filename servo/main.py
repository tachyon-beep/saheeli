"""Entry point for the Servo container."""

import os
import asyncio
from pathlib import Path

from saheeli.config import load_config, get_api_key

from .llm_interface import LLMInterface
from .agent import ServoAgent


def main() -> None:
    """Run the Servo agent inside the container."""
    cfg = load_config()
    api_key = get_api_key(cfg)
    llm = LLMInterface(cfg.api_base, api_key, cfg.model_name)
    workspace = Path("/workspace")
    task_id = os.getenv("TASK_ID", "task")
    agent = ServoAgent(task_id, workspace, llm)
    asyncio.run(agent.run())


if __name__ == "__main__":
    main()
