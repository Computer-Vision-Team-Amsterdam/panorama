# pylint: disable=R0903
"""
Module that should contain all (helper) models wrapping and/or abstracting API data
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, DirectoryPath, Field, HttpUrl

from panorama.client import PanoramaClient


class Link(BaseModel):
    """Pydantic model for individual links"""

    href: Optional[HttpUrl]


class PointGeometry(BaseModel):
    """Pydantic model for point geometry"""

    type: str
    coordinates: List[float]


class ImageSize(str, Enum):
    """Legal image sizes"""

    SMALL: Literal["small"] = "small"
    MEDIUM: Literal["medium"] = "medium"
    FULL: Literal["full"] = "full"


class PanoramaLinks(BaseModel):
    """Pydantic model for navigation links associated with a Panorama object"""

    self: Link
    equirectangular_full: Link
    equirectangular_medium: Link
    equirectangular_small: Link
    cubic_img_preview: Link
    thumbnail: Link
    adjacencies: Link


class LocationQuery(BaseModel):
    """
    latitude: latitude in degrees for the WGS84 standard, or x coordinate for the
        RD New projection
    longitude: longitude in degrees for the WGS84 standard, or y coordinate for the
        RD New projection
    radius: radius in meters surrounding the specified point
    srid can be either
        - 4326, which represents spatial data using longitude and latitude coordinates
            on the Earth's surface as defined in the WGS84 standard,
        - 28992, which represents the Dutch Amersfoort / RD New projection.
    """

    latitude: float
    longitude: float
    radius: int = 1
    srid: int = 4326


class Panorama(BaseModel):
    """Pydantic model to wrap Panorama objects"""

    links: PanoramaLinks = Field(alias="_links")
    cubic_img_baseurl: str
    cubic_img_pattern: str

    geometry: PointGeometry

    id: str = Field(alias="pano_id")
    timestamp: datetime
    filename: str

    surface_type: str

    mission_distance: int
    mission_type: str
    mission_year: str

    roll: float
    pitch: float
    heading: float

    tags: List[Optional[str]]

    @staticmethod
    async def get(panorama_id: str) -> Panorama:
        """Get an individual panorama object by remote id"""
        response = await PanoramaClient.get(panorama_id)
        if response.is_error:
            response.raise_for_status()
        return Panorama.parse_obj(response.json())

    # @staticmethod
    # async def list(
    #     location: Optional[LocationQuery] = None,
    #     timestamp_before: Optional[datetime] = None,
    #     timestamp_after: Optional[datetime] = None,
    #     limit_results: Optional[int] = None,
    # ) -> PagedPanoramasResponse:
    #     query = ""
    #     if location:
    #         query += f"&near={location.latitude},{location.longitude}" \
    #                  f"&radius={location.radius}" \
    #                  f"&srid={location.srid}"
    #     if timestamp_before:
    #         query += f"&timestamp_before={timestamp_before.timestamp()}"
    #     if timestamp_after:
    #         query += f"&timestamp_after={timestamp_after.timestamp()}"
    #     if limit_results:
    #         query += f"&limit_results={limit_results}"
    #     if query:
    #         query = f"?{query.lstrip('&')}"
    #
    #     response = await PanoramaClient.get(query)
    #     if response.is_error:
    #         response.raise_for_status()
    #     return PagedPanoramasResponse.parse_obj(response.json())
    #
    async def download_image(
        self,
        size: ImageSize = ImageSize.MEDIUM,
        output_location: DirectoryPath = Path("."),
    ) -> Panorama:
        """Download the selected panorama image to the specified location"""
        response = await PanoramaClient.get(
            getattr(self.links, f"equirectangular_{size.value}").href
        )

        with open(Path(output_location, self.filename), "wb") as file_header:
            file_header.write(response.content)

        return self


class PanoramasLinks(BaseModel):
    """
    Pydantic model for navigation links associated with a listed response of
    Panorama objects
    """

    self: Link
    previous: Link
    next: Link


class PagedPanoramasResponse(BaseModel):
    """
    Pydantic model to wrap paged API responses containing lists of Panorama objects
    """

    links: PanoramasLinks = Field(alias="_links")
    count: int
    embedded: Dict[str, List[Optional[Panorama]]] = Field(alias="_embedded")

    @property
    def panoramas(self) -> List[Optional[Panorama]]:
        """
        Helper property to make the accessing of the actual list of Panorama objects
        more user friendly
        """
        return self.embedded["panoramas"]

    async def _get_link(self, link: Optional[HttpUrl]) -> PagedPanoramasResponse:
        """Helper function to perform common tasks when calling the API"""
        if link is None:
            return self.copy(exclude={"embedded": "panoramas"})

        response = await PanoramaClient.get(link)
        return PagedPanoramasResponse.parse_obj(response.json())

    async def previous(self) -> PagedPanoramasResponse:
        """Get the previous page"""
        return await self._get_link(self.links.previous.href)

    async def next(self) -> PagedPanoramasResponse:
        """Get the next page"""
        return await self._get_link(self.links.next.href)
