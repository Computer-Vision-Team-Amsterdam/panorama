# pylint: disable=C0116,W0613
"""Tests for the client module"""
import asyncio
from datetime import date, datetime, time, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from haversine import Unit, haversine
from httpx import HTTPStatusError

from panorama.client import _AsyncPanoramaClient, _PanoramaClient
from panorama.models import LocationQuery, PagedPanoramasResponse, Panorama

pytestmark = pytest.mark.asyncio  # Required statement to run async tests


class TestAsyncClient:
    """Tests for the client class"""

    client = _AsyncPanoramaClient()
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

        the_mock.assert_called_once_with(Path(f"{panorama.id}.jpg"), "wb")

    @pytest.mark.vcr
    async def test_lists_panoramas(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas()
        assert response
        assert response.panoramas

    @pytest.mark.vcr
    async def test_lists_panoramas_at_location(self) -> None:
        location = LocationQuery(
            latitude=52.3626755978307, longitude=4.90769952140867, radius=0.5
        )
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            location=location
        )

        assert response.panoramas
        for panorama in response.panoramas:
            if panorama is not None:
                assert panorama.geometry.coordinates[0] == location.longitude
                assert panorama.geometry.coordinates[1] == location.latitude

    @pytest.mark.vcr
    async def test_lists_panoramas_only_before_timestamp(self) -> None:
        timestamp_before = date(2018, 1, 1)

        # This may be flaky without the option to sort the API response by timestamp
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            timestamp_before=timestamp_before
        )

        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp <= datetime.combine(
                timestamp_before, time(), timezone.utc
            )

    @pytest.mark.vcr
    async def test_lists_panoramas_only_after_timestamp(self) -> None:
        timestamp_after = date(2018, 1, 1)

        # This may be flaky without the option to sort the API response by timestamp
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            timestamp_after=timestamp_after
        )

        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp >= datetime.combine(
                timestamp_after, time(), timezone.utc
            )

    @pytest.mark.vcr
    async def test_lists_only_n_results(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            limit_results=2
        )

        assert len(response.panoramas) == 2

    @pytest.mark.vcr
    async def test_lists_results_with_combined_filters(self) -> None:
        location = LocationQuery(
            latitude=52.3626770908732, longitude=4.90774612505295, radius=10
        )
        timestamp_after = date(2018, 1, 1)
        timestamp_before = date(2020, 1, 1)

        response: PagedPanoramasResponse = await self.client.list_panoramas(
            location=location,
            timestamp_after=timestamp_after,
            timestamp_before=timestamp_before,
            limit_results=100,
        )

        assert response.count <= 100
        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp >= datetime.combine(
                timestamp_after, time(), timezone.utc
            )
            assert panorama.timestamp <= datetime.combine(
                timestamp_before, time(), timezone.utc
            )
            assert (
                haversine(
                    (location.longitude, location.latitude),
                    (
                        panorama.geometry.coordinates[0],
                        panorama.geometry.coordinates[1],
                    ),
                    Unit.METERS,
                )
                # Fuzz the distance to mitigate rounding errors resulting from
                # using WGS:84 coordinate system to calculate relatively small
                # distances. We are not validating the API's correctness anyway.
                # Use the RD New projection to achieve better results.
                <= 2 * location.radius
            )

    @pytest.mark.vcr
    async def test_lists_next_page(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas()
        next_page = await self.client.next_page(response)

        assert next_page.links.self.href == response.links.next.href
        assert response.panoramas != next_page.panoramas

    @pytest.mark.vcr
    async def test_raises_when_no_next_page(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            limit_results=1
        )
        with pytest.raises(ValueError) as err:
            await self.client.next_page(response)

            assert err.value == "No next page available"

    @pytest.mark.vcr
    async def test_lists_previous_page(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas()
        next_page = await self.client.next_page(response)
        first_page = await self.client.previous_page(next_page)

        assert first_page.links.self.href
        assert first_page.links.self.href.endswith("?page=1")
        assert response.panoramas == first_page.panoramas

    @pytest.mark.vcr
    async def test_raises_when_no_previous_page(self) -> None:
        response: PagedPanoramasResponse = await self.client.list_panoramas(
            limit_results=1
        )
        with pytest.raises(ValueError) as err:
            await self.client.previous_page(response)

            assert err.value == "No previous page available"


class TestClient:
    """Tests for the client class"""

    client = _PanoramaClient()
    panorama_id = "DPX2018000001-000001_pano_0000_000001"

    def test_client_has_default_absolute_base_url(self) -> None:
        assert self.client.base_url.is_absolute_url

    @pytest.mark.vcr
    def test_get_retrieves_model(self, event_loop: asyncio.AbstractEventLoop) -> None:
        assert isinstance(self.client.get_panorama(self.panorama_id), Panorama)

    @pytest.mark.vcr
    def test_get_throws_not_found(self, event_loop: asyncio.AbstractEventLoop) -> None:
        with pytest.raises(HTTPStatusError):
            self.client.get_panorama(f"invalid_{self.panorama_id}")

    @pytest.mark.vcr
    def test_download_retrieves_image(
        self, event_loop: asyncio.AbstractEventLoop
    ) -> None:
        panorama = self.client.get_panorama(self.panorama_id)
        with patch("builtins.open") as the_mock:
            self.client.download_image(panorama)

        the_mock.assert_called_once_with(Path(f"{panorama.id}.jpg"), "wb")

    @pytest.mark.vcr
    def test_lists_panoramas(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas()
        assert response
        assert response.panoramas

    @pytest.mark.vcr
    def test_lists_panoramas_at_location(self) -> None:
        location = LocationQuery(
            latitude=52.3626755978307, longitude=4.90769952140867, radius=0.5
        )
        response: PagedPanoramasResponse = self.client.list_panoramas(location=location)

        assert response.panoramas
        for panorama in response.panoramas:
            if panorama is not None:
                assert panorama.geometry.coordinates[0] == location.longitude
                assert panorama.geometry.coordinates[1] == location.latitude

    @pytest.mark.vcr
    def test_lists_panoramas_only_before_timestamp(self) -> None:
        timestamp_before = date(2018, 1, 1)

        # This may be flaky without the option to sort the API response by timestamp
        response: PagedPanoramasResponse = self.client.list_panoramas(
            timestamp_before=timestamp_before
        )

        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp <= datetime.combine(
                timestamp_before, time(), timezone.utc
            )

    @pytest.mark.vcr
    def test_lists_panoramas_only_after_timestamp(self) -> None:
        timestamp_after = date(2018, 1, 1)

        # This may be flaky without the option to sort the API response by timestamp
        response: PagedPanoramasResponse = self.client.list_panoramas(
            timestamp_after=timestamp_after
        )

        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp >= datetime.combine(
                timestamp_after, time(), timezone.utc
            )

    @pytest.mark.vcr
    def test_lists_only_n_results(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas(limit_results=2)

        assert len(response.panoramas) == 2

    @pytest.mark.vcr
    def test_lists_results_with_combined_filters(self) -> None:
        location = LocationQuery(
            latitude=52.3626770908732, longitude=4.90774612505295, radius=10
        )
        timestamp_after = date(2018, 1, 1)
        timestamp_before = date(2020, 1, 1)

        response: PagedPanoramasResponse = self.client.list_panoramas(
            location=location,
            timestamp_after=timestamp_after,
            timestamp_before=timestamp_before,
            limit_results=100,
        )

        assert response.count <= 100
        for panorama in response.panoramas:
            assert panorama
            assert panorama.timestamp >= datetime.combine(
                timestamp_after, time(), timezone.utc
            )
            assert panorama.timestamp <= datetime.combine(
                timestamp_before, time(), timezone.utc
            )
            assert (
                haversine(
                    (location.longitude, location.latitude),
                    (
                        panorama.geometry.coordinates[0],
                        panorama.geometry.coordinates[1],
                    ),
                    Unit.METERS,
                )
                # Fuzz the distance to mitigate rounding errors resulting from
                # using WGS:84 coordinate system to calculate relatively small
                # distances. We are not validating the API's correctness anyway.
                # Use the RD New projection to achieve better results.
                <= 2 * location.radius
            )

    @pytest.mark.vcr
    def test_lists_next_page(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas()
        next_page = self.client.next_page(response)

        assert next_page.links.self.href == response.links.next.href
        assert response.panoramas != next_page.panoramas

    @pytest.mark.vcr
    def test_raises_when_no_next_page(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas(limit_results=1)
        with pytest.raises(ValueError) as err:
            self.client.next_page(response)

            assert err.value == "No next page available"

    @pytest.mark.vcr
    def test_lists_previous_page(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas()
        next_page = self.client.next_page(response)
        first_page = self.client.previous_page(next_page)

        assert first_page.links.self.href
        assert first_page.links.self.href.endswith("?page=1")
        assert response.panoramas == first_page.panoramas

    @pytest.mark.vcr
    def test_raises_when_no_previous_page(self) -> None:
        response: PagedPanoramasResponse = self.client.list_panoramas(limit_results=1)
        with pytest.raises(ValueError) as err:
            self.client.previous_page(response)

            assert err.value == "No previous page available"
