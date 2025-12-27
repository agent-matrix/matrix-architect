from __future__ import annotations

from typing import Any, Dict, Optional
import httpx

class MatrixHubClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout_s: int = 60):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_s = timeout_s

    async def publish_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(f"{self.base_url}/manifests", json=manifest, headers=headers)
            r.raise_for_status()
            return r.json()
