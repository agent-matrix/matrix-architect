from __future__ import annotations

from typing import Dict, Any

def package_mcp_server(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Package/register an MCP server bundle.

    In the Matrix suite, matrix-system runs MCP servers. Matrix Architect can *produce* the
    server bundle + manifest for publishing to matrix-hub.
    """
    return {"ok": True, "manifest": manifest}
