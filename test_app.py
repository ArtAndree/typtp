"""Async tests for :func:`app.get_json`."""

import asyncio

import allure
import pytest
from aiohttp import web
from aiohttp.client_exceptions import ClientResponseError, ContentTypeError

from app import get_json


@pytest.fixture
def event_loop():
    """Provide an isolated asyncio loop for each async test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def json_server(aiohttp_server):
    """Start a local HTTP server so tests do not depend on the public internet."""
    app = web.Application()

    async def first_json(_request):
        return web.json_response({"message": "hello", "ok": True})

    async def second_json(_request):
        return web.json_response({"items": ["book", "pen"], "count": 2})

    async def unavailable(_request):
        return web.json_response({"error": "temporarily unavailable"}, status=503)

    async def invalid_json(_request):
        return web.Response(text="this is not JSON", content_type="text/plain")

    app.router.add_get("/first", first_json)
    app.router.add_get("/second", second_json)
    app.router.add_get("/unavailable", unavailable)
    app.router.add_get("/invalid-json", invalid_json)
    return await aiohttp_server(app)


@pytest.mark.asyncio
@allure.title("get_json returns JSON from the first URL")
@allure.description("Checks that a successful HTTP response is decoded to a Python object.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("aiohttp", "success")
async def test_get_json_first_url(json_server, event_loop):
    result = await get_json(str(json_server.make_url("/first")))

    assert result == {"message": "hello", "ok": True}


@pytest.mark.asyncio
@allure.title("get_json returns JSON from another URL")
@allure.description("Checks the helper against a second endpoint with a different JSON structure.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("aiohttp", "success", "different-url")
async def test_get_json_second_url(json_server, event_loop):
    result = await get_json(str(json_server.make_url("/second")))

    assert result == {"items": ["book", "pen"], "count": 2}


@pytest.mark.asyncio
@allure.title("get_json reports an HTTP error status")
@allure.description("Checks that a 503 response is raised as ClientResponseError.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("aiohttp", "error", "http-status")
async def test_get_json_http_error(json_server, event_loop):
    with pytest.raises(ClientResponseError) as error:
        await get_json(str(json_server.make_url("/unavailable")))

    assert error.value.status == 503


@pytest.mark.asyncio
@allure.title("get_json rejects a non-JSON response")
@allure.description("Checks that an incorrect response content type raises ContentTypeError.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("aiohttp", "error", "invalid-json")
async def test_get_json_invalid_json(json_server, event_loop):
    with pytest.raises(ContentTypeError):
        await get_json(str(json_server.make_url("/invalid-json")))
