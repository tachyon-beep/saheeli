import asyncio
from pathlib import Path
from .llm_interface import LLMInterface
from .agent import ServoAgent
from saheeli.config import load_config, get_api_key


def main() -> None:
    cfg = load_config()
    api_key = get_api_key(cfg)
    llm = LLMInterface(cfg.api_base, api_key, cfg.model_name)
    workspace = Path("/workspace")
    agent = ServoAgent("task", workspace, llm)
    asyncio.run(agent.run())


if __name__ == "__main__":
    main()
