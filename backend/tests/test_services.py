from datetime import date

import pytest

from app.errors import AppError
from app.models import Measurement
from app.parsing import parse_measurement, parse_menu, parse_nutrients
from app.services import MealService


class DummyClient:
    async def fetch_json(self, path, params):
        return {}


class DummySettings:
    meal_max_range_days = 31


def test_parse_menu_preserves_allergy_codes() -> None:
    items = parse_menu("잡곡밥(5)<br/>미역국(5.6)")
    assert items[0].name == "잡곡밥"
    assert items[0].allergyCodes == ["5"]
    assert items[1].allergyCodes == ["5", "6"]


def test_parse_measurement_returns_numeric_value() -> None:
    measurement = parse_measurement("열량 : 531.2 kcal", "열량")
    assert measurement == Measurement(label="열량", value=531.2, unit="kcal", sourceText="열량 : 531.2 kcal")


def test_parse_nutrients_keeps_text_for_unparsed_values() -> None:
    nutrients, source_text = parse_nutrients("탄수화물 : 30.5 g<br/>비타민: trace")
    assert len(nutrients) == 1
    assert source_text == "탄수화물 : 30.5 g<br/>비타민: trace"


def test_validate_range_rejects_reversed_dates() -> None:
    service = MealService(DummyClient(), DummySettings())
    with pytest.raises(AppError) as error:
        service.validate_range(date(2026, 8, 20), date(2026, 8, 10))
    assert error.value.detail["code"] == "INVALID_DATE_RANGE"


def test_validate_range_rejects_large_range() -> None:
    service = MealService(DummyClient(), DummySettings())
    with pytest.raises(AppError) as error:
        service.validate_range(date(2026, 8, 1), date(2026, 9, 1))
    assert error.value.detail["code"] == "DATE_RANGE_TOO_LARGE"


def test_utf8_korean_text_is_preserved() -> None:
    text = '{"schoolInfo":[{"head":[{"list_total_count":1},{"RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다."}}]},{"row":[{"ATPT_OFCDC_SC_CODE":"E10","SD_SCHUL_CODE":"7310057","SCHUL_NM":"인천고등학교","LCTN_SC_NM":"인천광역시","SCHUL_KND_SC_NM":"고등학교"}]}]}'
    encoded = text.encode("utf-8")
    assert encoded.decode("utf-8") == text
