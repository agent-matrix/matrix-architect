from __future__ import annotations

from typing import Dict, Any, Optional

from ..integrations.matrix_hub_client import MatrixHubClient

async def publish_manifest(hub_url: str, manifest: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    client = MatrixHubClient(base_url=hub_url, token=token)
    return await client.publish_manifest(manifest)

async def add_remote(hub_url: str, url: str, name: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Admin/operator action: registers a catalog remote for ingestion (token required on hardened Hub).
    """
    client = MatrixHubClient(base_url=hub_url, token=token)
    return await client.add_remote(url=url, name=name)

async def trigger_ingest(hub_url: str, url: Optional[str] = None, name: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Admin/operator action: triggers catalog ingest (token required on hardened Hub).
    """
    client = MatrixHubClient(base_url=hub_url, token=token)
    return await client.trigger_ingest(url=url, name=name)
