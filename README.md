# Panorama API Client

The Panorama API Client is a package that wraps the Datapunt Panoramas API.

## Requirements

- A recent version of Python 3. The project is being developed on Python 3.9, but should be compatible with some older minor versions.
- This project uses [Poetry](https://python-poetry.org/) as its package manager.

## Getting Started

Clone this repository and install the dependencies:

```shell
git clone git@github.com:Computer-Vision-Team-Amsterdam/panorama.git
poetry install
```

Use the `PanoramaClient` to browse retrieve Panoramas from the API:

```python
from panorama.client import PanoramaClient
from panorama import models

# Get the first page of panoramas
response: models.PagedPanoramasResponse = PanoramaClient.list_panoramas()

# Get the first panorama
panorama: models.Panorama = response.panoramas[0]

# Download the corresponding image to your machine
PanoramaClient.download_image(panorama, size=models.ImageSize.FULL)

# Get the next page of panoramas
next_page = PanoramaClient.next_page(response)
```