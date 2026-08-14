from collections.abc import AsyncGenerator

import pytest
from mcp.client.session import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.server.fastmcp import FastMCP


@pytest.fixture
def mcp_server(monkeypatch: pytest.MonkeyPatch) -> FastMCP:
    monkeypatch.setenv("NEIS_API_KEY", "test-key")
    from app.server import mcp

    return mcp


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client_session(mcp_server: FastMCP) -> AsyncGenerator[ClientSession]:
    async with create_connected_server_and_client_session(mcp_server, raise_exceptions=True) as session:
        yield session


@pytest.mark.anyio
async def test_tool_listing(client_session: ClientSession) -> None:
    tools = await client_session.list_tools()
    tool_names = {tool.name for tool in tools.tools}
    assert "search_schools" in tool_names
    assert "get_lunch_meals" in tool_names


@pytest.mark.anyio
async def test_search_tool_returns_validation_error(client_session: ClientSession) -> None:
    result = await client_session.call_tool("search_schools", {"query": "   "})
    assert result.structuredContent["ok"] is False
    assert result.structuredContent["code"] == "EMPTY_QUERY"


@pytest.mark.anyio
async def test_meal_tool_returns_missing_field_error(client_session: ClientSession) -> None:
    result = await client_session.call_tool(
        "get_lunch_meals",
        {"officeCode": "", "schoolCode": "7010569", "from_date": "2026-08-01", "to": "2026-08-31"},
    )
    assert result.structuredContent["ok"] is False
    assert result.structuredContent["code"] == "MISSING_FIELD"
