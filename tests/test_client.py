# pylint: disable=C0116,W0613
"""Tests for the client module"""
import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import HTTPStatusError

from panorama.client import _PanoramaClient
from panorama.models import LocationQuery, PagedPanoramasResponse, Panorama

pytestmark = pytest.mark.asyncio  # Required statement to run async tests


class TestClient:
    """Tests for the client class"""

    client = _PanoramaClient()
    panorama_id = "DPX2018000001-000001_pano_0000_000001"

    def test_client_has_default_absolute_base_url(self) -> None:
        assert self.client.base_url.is_absolute_url

    @pytest.mark.vcr
    async def test_get_retrieves_model(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        assert isinstance(await self.client.get_panorama(self.panorama_id), Panorama)

    @pytest.mark.vcr
    async def test_get_throws_not_found(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        with pytest.raises(HTTPStatusError):
            await self.client.get_panorama(f"invalid_{self.panorama_id}")

    @pytest.mark.vcr
    async def test_download_retrieves_image(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        panorama = await self.client.get_panorama(self.panorama_id)
        with patch("builtins.open") as the_mock:
            await self.client.download_image(panorama)

        the_mock.assert_called_once_with(Path(panorama.filename), "wb")

    @pytest.mark.vcr
    async def test_lists_panoramas(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas()
        assert response

    @pytest.mark.vcr
    async def test_lists_panoramas_at_location(self) -> None:
        location = LocationQuery(latitude=4.90765, longitude=52.36272, radius=1)
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            location=location
        )

        assert response.panoramas
        for panorama in response.panoramas:
            if panorama is not None:
                assert panorama.geometry.coordinates[0] == location.latitude
                assert panorama.geometry.coordinates[1] == location.longitude
