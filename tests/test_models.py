# pylint: disable=C0116,W0613
"""Tests for the models module"""
import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import HTTPStatusError

from panorama.models import Panorama

pytestmark = pytest.mark.asyncio


class TestPanorama:
    """Tests for the Panorama model and its methods"""

    panorama_id = "DPX2018000001-000001_pano_0000_000001"

    @pytest.mark.vcr()
    async def test_get_retrieves_model(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        assert isinstance(await Panorama.get(self.panorama_id), Panorama)

    @pytest.mark.vcr()
    async def test_get_throws_not_found(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        with pytest.raises(HTTPStatusError):
            await Panorama.get(f"invalid_{self.panorama_id}")

    @pytest.mark.vcr()
    async def test_download_retrieves_image(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        panorama = await Panorama.get(self.panorama_id)
        with patch("builtins.open") as the_mock:
            await panorama.download_image()

        the_mock.assert_called_once_with(Path(panorama.filename), "wb")
