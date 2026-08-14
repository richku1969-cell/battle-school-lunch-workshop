from __future__ import annotations

from app.clients import NeisClient
from app.config import get_settings
from app.errors import McpError, missing_field_error
from app.parsing import parse_iso_date
from app.services import MealService, SchoolService
from mcp.server.fastmcp import FastMCP

settings = get_settings()
mcp = FastMCP("School Lunch MCP", json_response=True)


def _school_service() -> SchoolService:
    return SchoolService(NeisClient(settings), settings)


def _meal_service() -> MealService:
    return MealService(NeisClient(settings), settings)


@mcp.tool()
async def search_schools(query: str) -> dict[str, object]:
    """학교 이름 일부를 입력받아 후보 학교와 식별 정보를 조회합니다."""
    try:
        result = await _school_service().search(query)
    except McpError as exc:
        return exc.to_payload()

    payload = result.model_dump(mode="json")
    payload["ok"] = True
    return payload


@mcp.tool()
async def get_lunch_meals(officeCode: str, schoolCode: str, from_date: str, to: str) -> dict[str, object]:
    """학교 식별 정보와 날짜 범위를 입력받아 중식 기준 급식 정보를 조회합니다."""
    try:
        if not officeCode:
            raise missing_field_error("officeCode")
        if not schoolCode:
            raise missing_field_error("schoolCode")
        parsed_from_date = parse_iso_date(from_date, "from")
        to_date = parse_iso_date(to, "to")
        result = await _meal_service().list_meals(officeCode, schoolCode, parsed_from_date, to_date)
    except McpError as exc:
        return exc.to_payload()

    payload = result.model_dump(mode="json")
    payload["ok"] = True
    return payload
