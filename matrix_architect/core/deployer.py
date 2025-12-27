from __future__ import annotations

from typing import Protocol, Dict, Any

class Deployer(Protocol):
    async def deploy(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        ...

class NoopDeployer:
    async def deploy(self, bundle: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": True, "message": "Noop deployer - nothing executed.", "bundle": bundle}
