from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from matrix_architect.integrations.matrix_hub_client import MatrixHubClient


class TestMatrixHubClientInit:
    """Tests for MatrixHubClient initialization."""

    def test_init_with_explicit_token(self):
        """Token passed explicitly should be used."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="explicit-token")
        assert client.token == "explicit-token"
        assert client.base_url == "https://hub.example.com"
        assert client.timeout_s == 60

    def test_init_strips_trailing_slash(self):
        """Base URL should have trailing slash stripped."""
        client = MatrixHubClient(base_url="https://hub.example.com/", token="test")
        assert client.base_url == "https://hub.example.com"

    @patch.dict(os.environ, {"MATRIX_HUB_TOKEN": "env-token"}, clear=True)
    def test_init_reads_matrix_hub_token_env(self):
        """Should read MATRIX_HUB_TOKEN from environment when token not provided."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        assert client.token == "env-token"

    @patch.dict(os.environ, {"MATRIX_TOKEN": "matrix-token"}, clear=True)
    def test_init_reads_matrix_token_env(self):
        """Should read MATRIX_TOKEN as fallback when MATRIX_HUB_TOKEN not set."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        assert client.token == "matrix-token"

    @patch.dict(os.environ, {"API_TOKEN": "api-token"}, clear=True)
    def test_init_reads_api_token_env(self):
        """Should read API_TOKEN as final fallback."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        assert client.token == "api-token"

    @patch.dict(os.environ, {"MATRIX_HUB_TOKEN": "primary", "MATRIX_TOKEN": "secondary"}, clear=True)
    def test_init_env_priority(self):
        """MATRIX_HUB_TOKEN should take priority over MATRIX_TOKEN."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        assert client.token == "primary"

    @patch.dict(os.environ, {"MATRIX_HUB_TOKEN": "env-token"}, clear=True)
    def test_init_explicit_overrides_env(self):
        """Explicit token should override environment variables."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="explicit")
        assert client.token == "explicit"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_no_token(self):
        """When no token available, should be None."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        assert client.token is None


class TestMatrixHubClientHeaders:
    """Tests for the _headers method."""

    def test_headers_with_token(self):
        """Headers should include Authorization when token is set."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="test-token")
        headers = client._headers()
        assert headers["Accept"] == "application/json"
        assert headers["Authorization"] == "Bearer test-token"

    @patch.dict(os.environ, {}, clear=True)
    def test_headers_without_token(self):
        """Headers should not include Authorization when token is None."""
        client = MatrixHubClient(base_url="https://hub.example.com")
        headers = client._headers()
        assert headers["Accept"] == "application/json"
        assert "Authorization" not in headers


class TestMatrixHubClientPublishManifest:
    """Tests for the publish_manifest method."""

    @pytest.mark.asyncio
    async def test_publish_manifest_legacy_success(self):
        """publish_manifest should succeed on legacy /manifests endpoint."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="test")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "manifest-123", "status": "published"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await client.publish_manifest({"name": "test-agent"})

            assert result == {"id": "manifest-123", "status": "published"}
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_manifest_404_returns_catalog_guidance(self):
        """When /manifests returns 404, should return catalog workflow guidance."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="test")

        mock_404_response = MagicMock()
        mock_404_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_404_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await client.publish_manifest({"name": "test-agent"})

            assert result["ok"] is False
            assert result["error"] == "manifest_publish_not_supported"
            assert "catalog-based" in result["detail"]
            assert "next_steps" in result


class TestMatrixHubClientAddRemote:
    """Tests for the add_remote method."""

    @pytest.mark.asyncio
    async def test_add_remote_success(self):
        """add_remote should POST to /catalog/remotes."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="admin-token")

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"name": "my-catalog", "url": "https://catalog.example.com"}'
        mock_response.json.return_value = {"name": "my-catalog", "url": "https://catalog.example.com"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await client.add_remote(url="https://catalog.example.com", name="my-catalog")

            assert result["name"] == "my-catalog"

    @pytest.mark.asyncio
    async def test_add_remote_permission_denied(self):
        """add_remote should raise PermissionError on 401/403."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="invalid")

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_response.json.return_value = {"error": "Forbidden"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with pytest.raises(PermissionError) as exc_info:
                await client.add_remote(url="https://catalog.example.com")

            assert "operator token" in str(exc_info.value)


class TestMatrixHubClientTriggerIngest:
    """Tests for the trigger_ingest method."""

    @pytest.mark.asyncio
    async def test_trigger_ingest_success(self):
        """trigger_ingest should POST to /catalog/ingest."""
        client = MatrixHubClient(base_url="https://hub.example.com", token="admin-token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "ingesting", "entities_added": 5}'
        mock_response.json.return_value = {"status": "ingesting", "entities_added": 5}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await client.trigger_ingest(url="https://catalog.example.com")

            assert result["status"] == "ingesting"
            assert result["entities_added"] == 5

    @pytest.mark.asyncio
    async def test_trigger_ingest_permission_denied(self):
        """trigger_ingest should raise PermissionError on 401."""
        client = MatrixHubClient(base_url="https://hub.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.json.return_value = {"error": "Unauthorized"}

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            with pytest.raises(PermissionError) as exc_info:
                await client.trigger_ingest(name="my-catalog")

            assert "operator token" in str(exc_info.value)
