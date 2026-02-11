from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from matrix_architect.tools import hub_tools


class TestPublishManifest:
    """Tests for the publish_manifest function."""

    @pytest.mark.asyncio
    async def test_publish_manifest_calls_client(self):
        """publish_manifest should delegate to MatrixHubClient."""
        with patch("matrix_architect.tools.hub_tools.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.publish_manifest.return_value = {"id": "test-123"}
            mock_client_cls.return_value = mock_client

            result = await hub_tools.publish_manifest(
                hub_url="https://hub.example.com",
                manifest={"name": "test-agent"},
                token="test-token",
            )

            mock_client_cls.assert_called_once_with(base_url="https://hub.example.com", token="test-token")
            mock_client.publish_manifest.assert_called_once_with({"name": "test-agent"})
            assert result == {"id": "test-123"}


class TestAddRemote:
    """Tests for the add_remote function."""

    @pytest.mark.asyncio
    async def test_add_remote_calls_client(self):
        """add_remote should delegate to MatrixHubClient."""
        with patch("matrix_architect.tools.hub_tools.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.add_remote.return_value = {"name": "my-remote", "url": "https://catalog.example.com"}
            mock_client_cls.return_value = mock_client

            result = await hub_tools.add_remote(
                hub_url="https://hub.example.com",
                url="https://catalog.example.com",
                name="my-remote",
                token="admin-token",
            )

            mock_client_cls.assert_called_once_with(base_url="https://hub.example.com", token="admin-token")
            mock_client.add_remote.assert_called_once_with(url="https://catalog.example.com", name="my-remote")
            assert result == {"name": "my-remote", "url": "https://catalog.example.com"}


class TestTriggerIngest:
    """Tests for the trigger_ingest function."""

    @pytest.mark.asyncio
    async def test_trigger_ingest_calls_client(self):
        """trigger_ingest should delegate to MatrixHubClient."""
        with patch("matrix_architect.tools.hub_tools.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.trigger_ingest.return_value = {"status": "complete", "entities_added": 10}
            mock_client_cls.return_value = mock_client

            result = await hub_tools.trigger_ingest(
                hub_url="https://hub.example.com",
                url="https://catalog.example.com",
                token="admin-token",
            )

            mock_client_cls.assert_called_once_with(base_url="https://hub.example.com", token="admin-token")
            mock_client.trigger_ingest.assert_called_once_with(url="https://catalog.example.com", name=None)
            assert result == {"status": "complete", "entities_added": 10}
