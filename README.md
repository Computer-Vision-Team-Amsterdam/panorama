# Panorama API Client

The Panorama API Client is a package that wraps the [Datapunt Panorama API](https://api.data.amsterdam.nl/panorama) of the Gemeente Amsterdam.

## Requirements

-   A recent version of Python 3. The project is being developed on Python 3.14, but should be compatible with some older minor versions.
-   Install the dependencies following the [instructions here](INSTALL.md).

## Getting Started

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
next_page: models.PagedPanoramasResponse = PanoramaClient.next_page(response)

# Pass different arguments to PanoramaClient.list_panoramas() to query
# location and date, and limit your results
from datetime import date

location = models.LocationQuery(
    latitude=52.3626770908732, longitude=4.90774612505295, radius=10
)
timestamp_after = date(2018, 1, 1)
timestamp_before = date(2020, 1, 1)

query_result: models.PagedPanoramasResponse = PanoramaClient.list_panoramas(
    location=location,
    timestamp_after=timestamp_after,
    timestamp_before=timestamp_before,
    limit_results=100,
)
```

Or use the `async` client with the same interface:

```python
import asyncio

from panorama.client import AsyncPanoramaClient
from panorama import models

# Start your event loop
loop = asyncio.get_event_loop()

# Get the first page of panoramas
response: models.PagedPanoramasResponse = loop.run_until_complete(AsyncPanoramaClient.list_panoramas())

```