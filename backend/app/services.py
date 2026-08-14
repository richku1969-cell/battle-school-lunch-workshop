from __future__ import annotations

from datetime import date
from typing import Any

from app.clients import NeisClient
from app.config import Settings
from app.errors import (
    date_range_too_large_error,
    empty_query_error,
    invalid_date_range_error,
    neis_invalid_response_error,
    neis_rate_limited_error,
    neis_unauthorized_error,
)
from app.models import Meal, MealResponse, SchoolSearchResponse, SchoolSummary
from app.parsing import format_ymd, parse_measurement, parse_menu, parse_nutrients, parse_ymd

SUCCESS_CODES = {"INFO-000"}
NO_DATA_CODES = {"INFO-200", "INFO-100"}
UNAUTHORIZED_CODES = {"ERROR-300"}
RATE_LIMIT_CODES = {"ERROR-337", "ERROR-338"}


def _extract_dataset(payload: dict[str, Any], key: str) -> tuple[int, list[dict[str, Any]]]:
    dataset = payload.get(key)
    if dataset is None:
        return 0, []
    if not isinstance(dataset, list):
        raise neis_invalid_response_error()

    head = next((item.get("head") for item in dataset if isinstance(item, dict) and "head" in item), None)
    rows = next((item.get("row") for item in dataset if isinstance(item, dict) and "row" in item), None)
    if not isinstance(head, list):
        raise neis_invalid_response_error()

    total = 0
    result_code: str | None = None
    for entry in head:
        if not isinstance(entry, dict):
            continue
        if "list_total_count" in entry:
            total = int(entry["list_total_count"])
        result = entry.get("RESULT")
        if isinstance(result, dict) and isinstance(result.get("CODE"), str):
            result_code = result["CODE"]

    if result_code in NO_DATA_CODES:
        return 0, []
    if result_code in UNAUTHORIZED_CODES:
        raise neis_unauthorized_error()
    if result_code in RATE_LIMIT_CODES:
        raise neis_rate_limited_error()
    if result_code is not None and result_code not in SUCCESS_CODES:
        raise neis_invalid_response_error()
    if rows is None:
        return total, []
    if not isinstance(rows, list):
        raise neis_invalid_response_error()
    return total, [row for row in rows if isinstance(row, dict)]


class SchoolService:
    def __init__(self, client: NeisClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def search(self, query: str) -> SchoolSearchResponse:
        normalized = query.strip()
        if not normalized:
            raise empty_query_error()

        payload = await self._client.fetch_json(
            "/hub/schoolInfo",
            {"pIndex": 1, "pSize": self._settings.school_page_size, "SCHUL_NM": normalized},
        )
        total, rows = _extract_dataset(payload, "schoolInfo")
        schools: list[SchoolSummary] = []
        for row in rows:
            office_code = row.get("ATPT_OFCDC_SC_CODE")
            school_code = row.get("SD_SCHUL_CODE")
            name = row.get("SCHUL_NM")
            if not office_code or not school_code or not name:
                continue
            schools.append(
                SchoolSummary(
                    officeCode=str(office_code),
                    schoolCode=str(school_code),
                    name=str(name),
                    region=str(row.get("LCTN_SC_NM") or ""),
                    schoolType=str(row.get("SCHUL_KND_SC_NM") or ""),
                )
            )

        limited = schools[: self._settings.school_result_limit]
        return SchoolSearchResponse(items=limited, total=total, hasMore=total > len(limited))


class MealService:
    def __init__(self, client: NeisClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def validate_range(self, from_date: date, to_date: date) -> None:
        if from_date > to_date:
            raise invalid_date_range_error()
        if (to_date - from_date).days + 1 > self._settings.meal_max_range_days:
            raise date_range_too_large_error(self._settings.meal_max_range_days)

    async def list_meals(self, office_code: str, school_code: str, from_date: date, to_date: date) -> MealResponse:
        self.validate_range(from_date, to_date)

        page = 1
        total = 1
        items: list[Meal] = []
        while len(items) < total:
            payload = await self._client.fetch_json(
                "/hub/mealServiceDietInfo",
                {
                    "pIndex": page,
                    "pSize": 100,
                    "ATPT_OFCDC_SC_CODE": office_code,
                    "SD_SCHUL_CODE": school_code,
                    "MMEAL_SC_CODE": "2",
                    "MLSV_FROM_YMD": format_ymd(from_date),
                    "MLSV_TO_YMD": format_ymd(to_date),
                },
            )
            total, rows = _extract_dataset(payload, "mealServiceDietInfo")
            if not rows:
                break
            for row in rows:
                date_text = row.get("MLSV_YMD")
                meal_type = row.get("MMEAL_SC_NM")
                if not date_text or not meal_type:
                    continue
                calories = parse_measurement(str(row.get("CAL_INFO") or ""), "열량")
                nutrients, nutrition_text = parse_nutrients(str(row.get("NTR_INFO") or ""))
                items.append(
                    Meal(
                        date=parse_ymd(str(date_text)),
                        mealType=str(meal_type),
                        menu=parse_menu(str(row.get("DDISH_NM") or "")),
                        calories=calories,
                        nutrients=nutrients,
                        nutritionText=nutrition_text,
                        origin=str(row.get("ORPLC_INFO")) if row.get("ORPLC_INFO") else None,
                    )
                )
            page += 1
            if len(rows) == 0:
                break

        items.sort(key=lambda meal: meal.date)
        return MealResponse(items=items)
