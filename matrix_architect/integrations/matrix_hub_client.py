from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
import os
import httpx

class MatrixHubClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout_s: int = 60):
        self.base_url = base_url.rstrip("/")
        # Non-destructive compatibility: if token not provided, try ecosystem env vars
        self.token = token or (
            os.getenv("MATRIX_HUB_TOKEN") or os.getenv("MATRIX_TOKEN") or os.getenv("API_TOKEN") or None
        )
        self.timeout_s = timeout_s

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _post_json(self, path: str, payload: Dict[str, Any]) -> Tuple[int, Any, str]:
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(f"{self.base_url}{path}", json=payload, headers=self._headers())
            text = r.text
            try:
                data = r.json()
            except Exception:
                data = {"raw": text}
            return r.status_code, data, text

    async def publish_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy behavior: POST /manifests (some older hubs may have this).

        Updated Matrix-Hub is catalog-based and typically does NOT expose /manifests.
        If /manifests is missing, return a helpful message and suggest catalog ingestion.
        """
        # 1) Try legacy endpoint
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.post(f"{self.base_url}/manifests", json=manifest, headers=self._headers())
            if r.status_code != 404:
                r.raise_for_status()
                return r.json()

        # 2) Try a future-compatible catalog endpoint (if added later)
        status, data, text = await self._post_json("/catalog/manifests", manifest)
        if status != 404:
            if status >= 400:
                raise httpx.HTTPStatusError(f"publish_manifest failed: {status} {text}", request=None, response=None)
            return data

        # 3) Fallback: explain the catalog workflow (non-destructive, explicit)
        return {
            "ok": False,
            "error": "manifest_publish_not_supported",
            "detail": (
                "This Matrix-Hub is catalog-based and does not accept direct manifest publishes. "
                "Publish the manifest to a catalog/remote URL and then ask Hub to ingest it "
                "(/catalog/remotes + /catalog/ingest)."
            ),
            "next_steps": {
                "1_publish_manifest_somewhere": "Commit to catalog repo or host manifest/index.json on a trusted URL",
                "2_add_remote_admin": "Use add_remote(url=...) (requires operator token)",
                "3_trigger_ingest_admin": "Use trigger_ingest(url=... or name=...) (requires operator token)",
            },
        }

    async def add_remote(self, url: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Admin helper for catalog-based Hub:
        POST /catalog/remotes (token required in hardened Hub)
        """
        payload: Dict[str, Any] = {"url": url}
        if name:
            payload["name"] = name
        status, data, text = await self._post_json("/catalog/remotes", payload)
        if status in (401, 403):
            raise PermissionError("add_remote requires operator token (set MATRIX_HUB_TOKEN)")
        if status >= 400:
            raise httpx.HTTPStatusError(f"add_remote failed: {status} {text}", request=None, response=None)
        return data

    async def trigger_ingest(self, url: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Admin helper for catalog-based Hub:
        POST /catalog/ingest (token required in hardened Hub)
        """
        payload: Dict[str, Any] = {}
        if url:
            payload["url"] = url
        if name:
            payload["name"] = name
        status, data, text = await self._post_json("/catalog/ingest", payload)
        if status in (401, 403):
            raise PermissionError("trigger_ingest requires operator token (set MATRIX_HUB_TOKEN)")
        if status >= 400:
            raise httpx.HTTPStatusError(f"trigger_ingest failed: {status} {text}", request=None, response=None)
        return data
