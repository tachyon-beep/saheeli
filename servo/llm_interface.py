from typing import List, Dict
import httpx


class LLMInterface:
    def __init__(self, api_base: str, api_key: str, model: str) -> None:
        self.client = httpx.AsyncClient(
            base_url=api_base, headers={"Authorization": f"Bearer {api_key}"}
        )
        self.model = model

    async def chat(self, messages: List[Dict]) -> Dict:
        payload = {"model": self.model, "messages": messages}
        resp = await self.client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()
