"""
httpx client to connect to the Panorama API

This module should contain all code related to network interactions with the Panorama
API
"""
from datetime import datetime
from pathlib import Path
from typing import Optional, Type, TypeVar

from httpx import AsyncClient
from pydantic import DirectoryPath

from panorama import models

T = TypeVar("T", bound=models.BaseModel)  # pylint: disable=C0103


class _PanoramaClient(AsyncClient):
    def __init__(
        self, base_url: str = "https://api.data.amsterdam.nl/panorama/panoramas"
    ) -> None:
        super().__init__(base_url=base_url)

    async def _get_or_raise(self, path: str, type_: Type[T]) -> T:
        """Helper method to retrieve and typecast data"""
        response = await self.get(path)
        if response.is_error:
            response.raise_for_status()
        return type_.parse_obj(response.json())

    async def get_panorama(self, panorama_id: str) -> models.Panorama:
        """Get an individual panorama object by remote id"""
        return await self._get_or_raise(panorama_id, models.Panorama)

    async def download_image(
        self,
        panorama: models.Panorama,
        size: models.ImageSize = models.ImageSize.MEDIUM,
        output_location: DirectoryPath = Path("."),
    ) -> models.Panorama:
        """Download the selected panorama image to the specified location"""
        response = await self.get(
            getattr(panorama.links, f"equirectangular_{size.value}").href
        )

        with open(Path(output_location, panorama.filename), "wb") as file_header:
            file_header.write(response.content)

        return panorama

    async def list_panoramas(
        self,
        location: Optional[models.LocationQuery] = None,
        timestamp_before: Optional[datetime] = None,
        timestamp_after: Optional[datetime] = None,
        limit_results: Optional[int] = None,
    ) -> models.PagedPanoramasResponse:
        """List and filter panorama objects"""
        query = ""
        if location:
            query += (
                f"&near={location.latitude},{location.longitude}"
                f"&radius={location.radius}"
                f"&srid={location.srid}"
            )
        if timestamp_before:
            query += f"&timestamp_before={timestamp_before.timestamp()}"
        if timestamp_after:
            query += f"&timestamp_after={timestamp_after.timestamp()}"
        if limit_results:
            query += f"&limit_results={limit_results}"
        if query:
            query = f"?{query.lstrip('&')}"

        return await self._get_or_raise(query, models.PagedPanoramasResponse)

    async def previous_page(
        self, page: models.PagedPanoramasResponse
    ) -> models.PagedPanoramasResponse:
        """Get the previous page"""
        if not page.links.previous.href:
            raise ValueError("No previous page available")
        return await self._get_or_raise(
            page.links.previous.href, models.PagedPanoramasResponse
        )

    async def next_page(
        self, page: models.PagedPanoramasResponse
    ) -> models.PagedPanoramasResponse:
        """Get the previous page"""
        if not page.links.next.href:
            raise ValueError("No next page available")
        return await self._get_or_raise(
            page.links.next.href, models.PagedPanoramasResponse
        )


PanoramaClient = _PanoramaClient()
