"""httpx client to connect to the Panorama API"""
from httpx import AsyncClient


class _PanoramaClient(AsyncClient):
    def __init__(
        self, base_url: str = "https://api.data.amsterdam.nl/panorama/panoramas"
    ) -> None:
        super().__init__(base_url=base_url)


PanoramaClient = _PanoramaClient()
