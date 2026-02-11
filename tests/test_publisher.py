from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from matrix_architect.core import publisher


class TestPublish:
    """Tests for the publish function."""

    @pytest.mark.asyncio
    async def test_publish_calls_client(self):
        """publish should delegate to MatrixHubClient.publish_manifest."""
        with patch("matrix_architect.core.publisher.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.publish_manifest.return_value = {"id": "manifest-123"}
            mock_client_cls.return_value = mock_client

            result = await publisher.publish(
                hub_url="https://hub.example.com",
                manifest={"name": "test-agent", "version": "1.0.0"},
                token="my-token",
            )

            mock_client_cls.assert_called_once_with("https://hub.example.com", token="my-token")
            mock_client.publish_manifest.assert_called_once_with({"name": "test-agent", "version": "1.0.0"})
            assert result == {"id": "manifest-123"}


class TestPublishViaCatalog:
    """Tests for the publish_via_catalog function."""

    @pytest.mark.asyncio
    async def test_publish_via_catalog_calls_add_remote_then_ingest(self):
        """publish_via_catalog should add remote then trigger ingest."""
        with patch("matrix_architect.core.publisher.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.add_remote.return_value = {"name": "my-catalog"}
            mock_client.trigger_ingest.return_value = {"status": "ingesting", "entities_added": 3}
            mock_client_cls.return_value = mock_client

            result = await publisher.publish_via_catalog(
                hub_url="https://hub.example.com",
                remote_url="https://catalog.example.com/index.json",
                name="my-catalog",
                token="admin-token",
            )

            mock_client_cls.assert_called_once_with("https://hub.example.com", token="admin-token")
            mock_client.add_remote.assert_called_once_with(url="https://catalog.example.com/index.json", name="my-catalog")
            mock_client.trigger_ingest.assert_called_once_with(url="https://catalog.example.com/index.json")
            assert result == {"status": "ingesting", "entities_added": 3}

    @pytest.mark.asyncio
    async def test_publish_via_catalog_without_name(self):
        """publish_via_catalog should work without explicit name."""
        with patch("matrix_architect.core.publisher.MatrixHubClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.add_remote.return_value = {"url": "https://catalog.example.com"}
            mock_client.trigger_ingest.return_value = {"status": "done"}
            mock_client_cls.return_value = mock_client

            result = await publisher.publish_via_catalog(
                hub_url="https://hub.example.com",
                remote_url="https://catalog.example.com",
            )

            mock_client.add_remote.assert_called_once_with(url="https://catalog.example.com", name=None)
            assert result == {"status": "done"}
