from __future__ import annotations

from typing import Dict, Any, Optional
from ..integrations.matrix_hub_client import MatrixHubClient

async def publish(hub_url: str, manifest: Dict[str, Any], *, token: Optional[str] = None) -> Dict[str, Any]:
    client = MatrixHubClient(hub_url, token=token)
    return await client.publish_manifest(manifest)

# Optional helpers for catalog-based Matrix-Hub (admin/operator usage)
async def publish_via_catalog(hub_url: str, remote_url: str, *, name: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    client = MatrixHubClient(hub_url, token=token)
    await client.add_remote(url=remote_url, name=name)
    return await client.trigger_ingest(url=remote_url)
