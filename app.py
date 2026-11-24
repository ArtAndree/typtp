"""Small asynchronous HTTP helper used by the aiohttp testing assignment."""

from typing import Any

import aiohttp


async def get_json(url: str) -> Any:
    """Fetch *url* and return its JSON response.

    Raises aiohttp.ClientResponseError for non-success HTTP status codes and
    aiohttp.ContentTypeError (or a JSON decoding error) when the response body
    is not valid JSON.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
