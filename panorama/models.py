# pylint: disable=R0903
"""
This module should contain all (helper) models wrapping and/or abstracting API data
"""
from __future__ import annotations

import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


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

    srid can be either:
        - 4326, which represents spatial data using longitude and latitude coordinates
            on the Earth's surface as defined in the WGS84 standard,
        - 28992, which represents the Dutch Amersfoort / RD New projection.
    """

    latitude: float
    longitude: float
    radius: float = 1.0
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
