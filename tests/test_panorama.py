# pylint: disable=C0116
"""Tests for the Panorama API client"""
from panorama import __version__


def test_version() -> None:
    assert __version__ == "0.2.2"
