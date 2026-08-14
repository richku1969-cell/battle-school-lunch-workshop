from datetime import date

from pydantic import BaseModel, ConfigDict


class SchoolSummary(BaseModel):
    officeCode: str
    schoolCode: str
    name: str
    region: str
    schoolType: str


class SchoolSearchResponse(BaseModel):
    items: list[SchoolSummary]
    total: int
    hasMore: bool


class MenuItem(BaseModel):
    name: str
    allergyCodes: list[str]


class Measurement(BaseModel):
    label: str
    value: float
    unit: str
    sourceText: str


class Meal(BaseModel):
    date: date
    mealType: str
    menu: list[MenuItem]
    calories: Measurement | None = None
    nutrients: list[Measurement]
    nutritionText: str | None = None
    origin: str | None = None

    model_config = ConfigDict(json_encoders={date: lambda value: value.isoformat()})


class MealResponse(BaseModel):
    items: list[Meal]
