from collections.abc import Iterable

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Iterable[object] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        detail: dict[str, object] = {"code": code, "message": message}
        if details is not None:
            detail["details"] = list(details)
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def empty_query_error() -> AppError:
    return AppError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code="EMPTY_QUERY", message="학교 검색어를 입력해 주세요.")


def invalid_date_range_error() -> AppError:
    return AppError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code="INVALID_DATE_RANGE", message="시작일은 종료일보다 늦을 수 없습니다.")


def date_range_too_large_error(max_days: int) -> AppError:
    return AppError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, code="DATE_RANGE_TOO_LARGE", message=f"조회 기간은 최대 {max_days}일까지만 가능합니다.")


def neis_unauthorized_error() -> AppError:
    return AppError(status_code=status.HTTP_502_BAD_GATEWAY, code="NEIS_UNAUTHORIZED", message="현재 급식 서비스를 조회할 수 없습니다.")


def neis_invalid_response_error() -> AppError:
    return AppError(status_code=status.HTTP_502_BAD_GATEWAY, code="NEIS_INVALID_RESPONSE", message="외부 급식 서비스 응답을 처리할 수 없습니다.")


def neis_timeout_error() -> AppError:
    return AppError(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="NEIS_TIMEOUT",
        message="급식 서비스 응답이 지연되고 있습니다.",
        headers={"Retry-After": "30"},
    )


def neis_rate_limited_error() -> AppError:
    return AppError(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        code="NEIS_RATE_LIMITED",
        message="요청이 많아 잠시 후 다시 시도해 주세요.",
        headers={"Retry-After": "60"},
    )
