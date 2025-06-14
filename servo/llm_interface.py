"""Wrapper around the LLM HTTP API."""

from typing import List, Dict
import httpx


class LLMInterface:
    """Minimal asynchronous client for chatting with an LLM."""

    def __init__(self, api_base: str, api_key: str, model: str) -> None:
        """Create a new interface for the given endpoint and model."""
        self.test_mode = not api_key
        self.model = model
        if not self.test_mode:
            self.client = httpx.AsyncClient(
                base_url=api_base, headers={"Authorization": f"Bearer {api_key}"}
            )
        else:
            self.counter = 0

    async def chat(self, messages: List[Dict]) -> Dict:
        """Send chat messages to the model and return the response payload."""
        if self.test_mode:
            self.counter += 1
            if self.counter == 1:
                return {
                    "tool": "create_file",
                    "args": {
                        "path": "result.txt",
                        "content": "Hello from Saheeli's Servo!",
                    },
                }
            else:
                return {"tool": "task_complete", "args": {"summary": "done"}}
        payload = {"model": self.model, "messages": messages}
        resp = await self.client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()
