import os
from datetime import date

os.environ.setdefault("NEIS_API_KEY", "test-api-key")

from fastapi.testclient import TestClient

from app.main import app, get_meal_service, get_school_service
from app.models import Meal, MealResponse, MenuItem, SchoolSearchResponse, SchoolSummary


class StubSchoolService:
    async def search(self, query: str) -> SchoolSearchResponse:
        return SchoolSearchResponse(
            items=[SchoolSummary(officeCode="B10", schoolCode="7010569", name="테스트고", region="서울", schoolType="고등학교")],
            total=1,
            hasMore=False,
        )


class StubMealService:
    async def list_meals(self, office_code: str, school_code: str, from_date: date, to_date: date) -> MealResponse:
        return MealResponse(
            items=[
                Meal(
                    date=date(2026, 8, 14),
                    mealType="중식",
                    menu=[MenuItem(name="카레라이스", allergyCodes=["2", "5"])],
                    nutrients=[],
                )
            ]
        )


app.dependency_overrides[get_school_service] = lambda: StubSchoolService()
app.dependency_overrides[get_meal_service] = lambda: StubMealService()
client = TestClient(app)


def test_search_schools() -> None:
    response = client.get("/api/v1/schools", params={"name": "테스트"})
    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "테스트고"


def test_get_meals() -> None:
    response = client.get(
        "/api/v1/meals",
        params={"officeCode": "B10", "schoolCode": "7010569", "from": "2026-08-01", "to": "2026-08-31"},
    )
    assert response.status_code == 200
    assert response.json()["items"][0]["mealType"] == "중식"
