from __future__ import annotations

from datetime import date

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.clients import NeisClient
from app.config import Settings, get_settings
from app.models import MealResponse, SchoolSearchResponse
from app.services import MealService, SchoolService

app = FastAPI(title="School Lunch Backend", version="0.1.0")

settings = get_settings()
if settings.frontend_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )


def get_school_service(config: Settings = Depends(get_settings)) -> SchoolService:
    return SchoolService(NeisClient(config), config)


def get_meal_service(config: Settings = Depends(get_settings)) -> MealService:
    return MealService(NeisClient(config), config)


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/api/v1/schools", response_model=SchoolSearchResponse)
async def search_schools(
    name: str = Query(...),
    service: SchoolService = Depends(get_school_service),
) -> SchoolSearchResponse:
    return await service.search(name)


@app.get("/api/v1/meals", response_model=MealResponse)
async def get_meals(
    officeCode: str = Query(...),
    schoolCode: str = Query(...),
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    service: MealService = Depends(get_meal_service),
) -> MealResponse:
    return await service.list_meals(officeCode, schoolCode, from_, to)
