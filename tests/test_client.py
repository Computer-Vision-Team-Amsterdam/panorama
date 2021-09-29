# pylint: disable=C0116,R0903
"""Tests for the client module"""
from panorama.client import _PanoramaClient


class TestClient:
    """Tests for the client class"""

    @staticmethod
    def test_client_has_default_absolute_base_url() -> None:
        client = _PanoramaClient()
        assert client.base_url.is_absolute_url
