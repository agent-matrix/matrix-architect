from __future__ import annotations

from typing import Any, Dict, Optional
import httpx

class MatrixAIClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout_s: int = 120):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_s = timeout_s

    async def plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(f"{self.base_url}/plan", json=payload, headers=headers)
            r.raise_for_status()
            return r.json()

    async def code(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(f"{self.base_url}/code", json=payload, headers=headers)
            r.raise_for_status()
            return r.json()
