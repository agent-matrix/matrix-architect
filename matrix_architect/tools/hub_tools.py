from __future__ import annotations

from typing import Dict, Any, Optional

from ..integrations.matrix_hub_client import MatrixHubClient

async def publish_manifest(hub_url: str, manifest: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    client = MatrixHubClient(base_url=hub_url, token=token)
    return await client.publish_manifest(manifest)
